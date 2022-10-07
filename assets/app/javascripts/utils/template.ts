export let mergeClasses = (args: any, classNameList: string[]): any => {
    if (args.className) {
        let argsClassNames = args.className.split(" ");
        argsClassNames = [...argsClassNames, ...classNameList];
        args.className = argsClassNames.join(" ");
    } else {
        args.className = classNameList.join(" ");
    }

    return args;
};

export let mergeDatasets = (args: any, dataset: any): any => {
    if (!args.dataset) {
        args.dataset = {};
    }
    args.dataset = { ...args.dataset, ...dataset };
    return args;
};
