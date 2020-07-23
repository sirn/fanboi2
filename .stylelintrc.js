"use strict";

/**
 * @param {String} block
 * @param {Object} [presetOptions]
 * @param {String} [presetOptions.namespace]
 * @returns {RegExp}
 */
function bemSelector(block, presetOptions) {
    const ns =
        presetOptions && presetOptions.namespace ? `${presetOptions.namespace}-` : "";
    const WORD = "[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*";
    const element = `(?:__${WORD})?`;
    const modifier = `(?:--${WORD}){0,2}`;
    const attribute = "(?:\\[.+\\])?";
    return new RegExp(`^\\.${ns}${block}${element}${modifier}${attribute}$`);
}

module.exports = {
    extends: "stylelint-config-recommended",
    plugins: [
        "stylelint-selector-bem-pattern",
        "stylelint-no-unsupported-browser-features",
    ],
    rules: {
        "at-rule-no-unknown": [
            true,
            {
                ignoreAtRules: ["util", "lost", "import-normalize"],
            },
        ],
        "property-no-unknown": [
            true,
            {
                ignoreProperties: ["lost-util", "lost-column", "lost-flex-container"],
            },
        ],
        "plugin/selector-bem-pattern": {
            preset: "bem",
            utilitySelectors: "^\\.util-([a-zA-Z-_]+)*$",
            componentSelectors: bemSelector,
        },
    },
};
