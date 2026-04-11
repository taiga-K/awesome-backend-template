// root の openapi.yaml は entrypoint に限定し、
// 各 path の本体は分割ファイルへ逃がす運用を強制する。
function rootPathsRefOnly() {
  return {
    Root: {
      leave(root, ctx) {
        const paths = root.paths || {};

        for (const [pathKey, pathItem] of Object.entries(paths)) {
          const keys = Object.keys(pathItem || {});
          if (keys.length === 1 && keys[0] === '$ref') {
            continue;
          }

          ctx.report({
            message:
              'ルートの paths には inline operation を書かず、$ref で分割ファイルを参照してください。',
            location: ctx.location.child('paths').child(pathKey),
          });
        }
      },
    },
  };
}

// Redocly 側では local/<rule-name> として参照される。
export default function localRulesPlugin() {
  return {
    id: 'local',
    rules: {
      oas3: {
        'root-paths-ref-only': rootPathsRefOnly,
      },
    },
  };
}
