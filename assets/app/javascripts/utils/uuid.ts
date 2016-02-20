/* Derived from original source code by Jed Schmidt:
 * https://gist.github.com/jed/982883
 */

const template = [1e7, 1e3, 4e3, 8e3, 1e11].join("-");

export function generateUuid(): string {
    return template.replace(/[018]/g, function(str: string): string {
        var base = parseInt(str);
        return (base ^ Math.random() * 16 >> base/4).toString(16);
    });
}
