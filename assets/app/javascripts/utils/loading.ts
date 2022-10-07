import { addClass, removeClass } from "./elements";

export class LoadingState {
    isLoading: boolean = false;

    bind(fn: () => Promise<any>, buttonElement?: Element): void {
        if (!this.isLoading) {
            this.isLoading = true;

            if (buttonElement) {
                addClass(buttonElement, ["btn--loading"]);
            }

            fn()
                .then(() => {
                    this.unbind(buttonElement);
                })
                .catch(() => {
                    this.unbind(buttonElement);
                });
        }
    }

    private unbind(buttonElement?: Element) {
        this.isLoading = false;

        if (buttonElement) {
            removeClass(buttonElement, ["btn--loading"]);
        }
    }
}
