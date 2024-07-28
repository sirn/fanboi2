module.exports = {
    content: [
        "./fanboi2/templates/**/*.jinja2",
        "./assets/scripts/**/*.ts"
    ],
    theme: {
        extend: {
            colors: {
                'scarlet': {
                    '50': 'oklch(97.36% 0.02 58.64)',
                    '100': 'oklch(93.83% 0.04 56.93)',
                    '200': 'oklch(87.17% 0.08 51.11)',
                    '300': 'oklch(79.18% 0.13 47.93)',
                    '400': 'oklch(70.71% 0.19 40.13)',
                    '500': 'oklch(66.14% 0.23 34.87)',
                    '600': 'oklch(63.80% 0.24 31.81)',
                    '700': 'oklch(53.39% 0.21 30.66)',
                    '800': 'oklch(45.34% 0.17 29.85)',
                    '900': 'oklch(39.08% 0.14 29.76)',
                    '950': 'oklch(25.47% 0.09 29.02)',
                },
                'porcelain': {
                    '50': 'oklch(97.74% 0.00 236.50)',
                    '100': 'oklch(96.20% 0.01 239.82)',
                    '200': 'oklch(89.31% 0.02 234.52)',
                    '300': 'oklch(80.01% 0.03 231.42)',
                    '400': 'oklch(68.81% 0.05 231.36)',
                    '500': 'oklch(59.71% 0.06 231.23)',
                    '600': 'oklch(51.24% 0.05 235.42)',
                    '700': 'oklch(44.44% 0.05 235.58)',
                    '800': 'oklch(39.91% 0.04 234.58)',
                    '900': 'oklch(36.11% 0.03 237.93)',
                    '950': 'oklch(27.55% 0.02 245.87)',
                },

            },
        },
    },
    plugins: [
        require("@tailwindcss/forms"),
        require("@tailwindcss/aspect-ratio"),
        require("@tailwindcss/typography"),
        require("@tailwindcss/container-queries"),
    ],
}
