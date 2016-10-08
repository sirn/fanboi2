import {addClass, removeClass} from './elements';


export class LoadingState {
    isLoading: boolean;

    bind(buttonElement: Element | null, fn: (() => Promise<any>)): void {
        let self = this;
        if (!this.isLoading) {
            this.isLoading = true;
            if (buttonElement) {
                addClass(buttonElement, 'js-button-loading');
            }

            fn().
                then(function() { self.unbind(buttonElement); }).
                catch(function() { self.unbind(buttonElement); });
        }
    }

    private unbind(buttonElement: Element | null) {
        this.isLoading = false;
        if (buttonElement) {
            removeClass(buttonElement, 'js-button-loading');
        }
    }
}
