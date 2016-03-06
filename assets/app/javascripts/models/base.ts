import {NotImplementedError, ResourceError} from '../utils/errors';


export interface IModelData {
    [key: string]: any;
}


export class Model {
    constructor(data: IModelData) {
        this.throwError(data);
        this.serialize(data);
    }

    protected serialize(data: IModelData) {
        throw new NotImplementedError;
    }

    private throwError(data: IModelData) {
        if (data['type'] == 'error') {
            throw new ResourceError(data['message']);
        }
    }

    static assertType(data: IModelData, type: string) {
        if (data['type'] != type) {
            throw new ResourceError(
                `Expected ${type} type but got ${data['type']}.`
            );
        }
    }
}
