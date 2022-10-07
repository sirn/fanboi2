"use strict";

function bemSelector(block, opt) {
    const ns = opt && opt.namespace ? `${opt.namespace}-` : "";
    const WORD = "[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*";
    const element = `(?:__${WORD})?`;
    const modifier = `(?:--${WORD}){0,2}`;
    const attribute = "(?:\\[.+\\])?";
    return new RegExp(`^\\.${ns}${block}${element}${modifier}${attribute}$`);
}

module.exports = {
    extends: "stylelint-config-recommended-scss",
    plugins: [
        "stylelint-selector-bem-pattern",
        "stylelint-no-unsupported-browser-features",
    ],
    rules: {
        "scss/at-rule-no-unknown": [
            true,
            {
                ignoreAtRules: ["util", "import-normalize"],
            },
        ],
        "plugin/selector-bem-pattern": {
            preset: "bem",
            utilitySelectors: "^\\.u-([a-zA-Z-_][a-zA-Z0-9-_]+)*$",
            componentSelectors: bemSelector,
        },
    },
};
