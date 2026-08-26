// npm install react-bootstrap bootstrap
import "bootstrap/dist/css/bootstrap.min.css";
import {Button, ButtonToolbar} from "react-bootstrap";
export default function MainPage(){
    return (
        <div>
            <ButtonToolbar>
                <Button variant={"primary"}>primary</Button>
                <Button variant={"outline-secondary"}>outline secondary</Button>
                <Button variant={"success"}>success</Button>
                <Button variant={"warning"}>warning</Button>
                <Button variant={"danger"}>danger</Button>
                <Button variant={"info"}>info</Button>
                <Button variant={"light"}>light</Button>
                <Button variant={"dark"}>dark</Button>
                <Button variant={"link"}>link</Button>
            </ButtonToolbar>
        </div>
    );
}