const monthNames = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
];

export class DateFormatter {
    date: Date;

    constructor(date: Date) {
        this.date = date;
    }

    public toString(): string {
        let year = this.date.getFullYear();
        let month = monthNames[this.date.getMonth()];
        let date = `00${this.date.getDate()}`.slice(-2);
        let hour = `00${this.date.getHours()}`.slice(-2);
        let minute = `00${this.date.getMinutes()}`.slice(-2);
        let second = `00${this.date.getSeconds()}`.slice(-2);
        let dateFormatted = `${month} ${date}, ${year}`;
        let timeFormatted = `${hour}:${minute}:${second}`;
        return `${dateFormatted} at ${timeFormatted}`;
    }
}