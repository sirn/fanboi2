import {addClass, removeClass} from './elements';


export class LoadingState {
    isLoading: boolean;

    bind(buttonElement: Element, fn: (() => Promise<any>)): void {
        let self = this;
        if (!this.isLoading) {
            this.isLoading = true;
            addClass(buttonElement, 'js-button-loading');
            fn().
                then(function() { self.unbind(buttonElement); }).
                catch(function() { self.unbind(buttonElement); });
        }
    }

    private unbind(buttonElement: Element) {
        this.isLoading = false;
        removeClass(buttonElement, 'js-button-loading');
    }
}
