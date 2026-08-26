export default function MyStyle(){
    const styles = {
        fontSize:26,
        fontWeight:700,
        color:'blue',
        backgroundColor:'yellowgreen'
    };

    return(
        <div>
            <h1 style={{color:'red'}}>Hello Inline Style</h1>
            <p style={styles}>Java Script Object Style</p>
            <span>Use Style Sheet</span>
            <h1 className="App-title">Use ClassName</h1>
        </div>
    );
}