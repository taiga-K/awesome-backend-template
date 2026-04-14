# XML とシリアライゼーションの堅牢化

- `rule_id`: `codeguard-0-xml-and-serialization`
- 原題: XML security and safe deserialization (DTD/XXE hardening, schema validation, no unsafe native deserialization)

XML およびシリアライズされたデータの安全な解析・処理を行い、XXE、エンティティ展開、SSRF、DoS、プラットフォーム横断の不安全なデシリアライゼーションを防ぐ。

### XML パーサの堅牢化
- 既定で DTD と外部エンティティを無効にする。DOCTYPE 宣言を拒否する。
- ローカルで信頼できる XSD に対して厳密に検証する。明示的な上限（サイズ、深さ、要素数）を設定する。
- リゾルバのアクセスをサンドボックス化またはブロックする。解析中にネットワーク取得を行わない。予期しない DNS 活動を監視する。

#### Java
一般的な原則:
```java
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
```

DTD を無効にすると XXE および Billion Laughs 攻撃を防げる。DTD を無効にできない場合は、パーサ固有の方法で外部エンティティを無効にする。

### Java

Java のパーサは既定で XXE が有効になっている。

DocumentBuilderFactory / SAXParserFactory / DOM4J:

```java
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
String FEATURE = null;
try {
    // 主な防御 — DTD を完全に禁止
    FEATURE = "http://apache.org/xml/features/disallow-doctype-decl";
    dbf.setFeature(FEATURE, true);
    dbf.setXIncludeAware(false);
} catch (ParserConfigurationException e) {
    logger.info("ParserConfigurationException was thrown. The feature '" + FEATURE
    + "' is not supported by your XML processor.");
}
```

DTD を完全に無効にできない場合:

```java
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
String[] featuresToDisable = {
    "http://xml.org/sax/features/external-general-entities",
    "http://xml.org/sax/features/external-parameter-entities",
    "http://apache.org/xml/features/nonvalidating/load-external-dtd"
};

for (String feature : featuresToDisable) {
    try {    
        dbf.setFeature(feature, false); 
    } catch (ParserConfigurationException e) {
        logger.info("ParserConfigurationException was thrown. The feature '" + feature
        + "' is probably not supported by your XML processor.");
    }
}
dbf.setXIncludeAware(false);
dbf.setExpandEntityReferences(false);
dbf.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
```

#### .NET
```csharp
var settings = new XmlReaderSettings { DtdProcessing = DtdProcessing.Prohibit, XmlResolver = null };
var reader = XmlReader.Create(stream, settings);
```

#### Python
```python
from defusedxml import ElementTree as ET
ET.parse('file.xml')
# または lxml
from lxml import etree
parser = etree.XMLParser(resolve_entities=False, no_network=True)
tree = etree.parse('filename.xml', parser)
```

### 安全な XSLT / Transformer の利用
- `ACCESS_EXTERNAL_DTD` と `ACCESS_EXTERNAL_STYLESHEET` を空に設定する。リモートリソースの読み込みを避ける。

### デシリアライゼーションの安全性
- 信頼できないネイティブオブジェクトをデシリアライズしない。スキーマ検証付き JSON を優先する。
- 解析前にサイズ/構造の上限を強制する。厳密な許可リストがない限り多型タイプを拒否する。
- 言語固有:
  - PHP: `unserialize()` を避け、`json_decode()` を使う。
  - Python: `pickle` と不安全な YAML を避ける（`yaml.safe_load` のみ）。
  - Java: `ObjectInputStream#resolveClass` をオーバーライドして許可リスト化する。Jackson のデフォルト型付与を有効にしない。XStream の許可リストを使う。
  - .NET: `BinaryFormatter` を避け、`DataContractSerializer` または JSON.NET では `TypeNameHandling=None` とした `System.Text.Json` を優先する。
- 該当する場合はシリアライズされたペイロードに署名し検証する。デシリアライゼーションの失敗と異常をログに記録しアラートする。

### 実装チェックリスト
- DTD オフ。外部エンティティ無効。厳密なスキーマ検証。パーサ上限の設定。
- 解析中のネットワークアクセスなし。リゾルバを制限。監査の実施。
- 不安全なネイティブデシリアライゼーションなし。対応形式は厳密な許可リストとスキーマ検証。
- ライブラリの定期更新と、XXE/デシリアライゼーション用ペイロードを用いたテスト。
