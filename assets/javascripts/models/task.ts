import { Model, IModelData } from "./base";
import { CancellableToken } from "../utils/cancellable";
import { ResourceError } from "../utils/errors";
import { request } from "../utils/request";

enum Statuses {
    Queued,
    Pending,
    Started,
    Retry,
    Failure,
    Success,
}

export class Task extends Model {
    type: string;
    id: string;
    path: string;
    status: Statuses;
    data: { [key: string]: any };

    serialize(data: IModelData) {
        Model.assertType(data, "task");

        this.type = data["type"];
        this.id = data["id"];
        this.path = data["path"];
        this.data = data["data"];

        switch (data["status"]) {
            case "queued":
                this.status = Statuses.Queued;
                break;
            case "pending":
                this.status = Statuses.Pending;
                break;
            case "started":
                this.status = Statuses.Started;
                break;
            case "retry":
                this.status = Statuses.Retry;
                break;
            case "failure":
                this.status = Statuses.Failure;
                break;
            case "success":
                this.status = Statuses.Success;
                break;
        }
    }

    static queryId(id: string, token?: CancellableToken): Promise<Task> {
        return request("GET", `/api/1.0/tasks/${id}/`, {}, token).then(
            (resp: string) => {
                return new Task(JSON.parse(resp));
            },
        );
    }

    static waitFor(id: string, token?: CancellableToken): Promise<Task> {
        return Task.queryId(id, token).then((task: Task) => {
            if (task.status == Statuses.Success) {
                return task;
            } else if (task.status == Statuses.Failure) {
                throw new ResourceError("Task could not be completed.");
            } else {
                return Task.waitFor(id, token);
            }
        });
    }
}
