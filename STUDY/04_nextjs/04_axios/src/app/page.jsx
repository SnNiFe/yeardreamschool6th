import SendList from "@/app/SendList";

export default function Page(){

    const url = 'https://jsonplaceholder.typicode.com/posts/';

    return (
        <div>
            <SendList url={url} />
        </div>
    );
}