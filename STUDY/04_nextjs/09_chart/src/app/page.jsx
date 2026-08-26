import Link from "next/link";

export default function Home(){
    return (
        <div>
            <h3>Chart Library</h3>
            <p><Link href="/bar">Bar Chart</Link></p>
            <p><Link href="/line">Line Chart</Link></p>
            <p><Link href="/pie">Pie Chart</Link></p>
            <p><Link href="/scatter">Scatter Chart</Link></p>
        </div>
    );
}