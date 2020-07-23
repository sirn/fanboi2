const monthNames = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
];

export let formatDate = (date: Date): string => {
    let yyyy = date.getFullYear();
    let mmm = monthNames[date.getMonth()];
    let dd = `00${date.getDate()}`.slice(-2);
    let hh = `00${date.getHours()}`.slice(-2);
    let nn = `00${date.getMinutes()}`.slice(-2);
    let ss = `00${date.getSeconds()}`.slice(-2);
    let dateFormatted = `${mmm} ${dd}, ${yyyy}`;
    let timeFormatted = `${hh}:${nn}:${ss}`;

    return `${dateFormatted} at ${timeFormatted}`;
};
