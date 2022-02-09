import logo from './tacogar.png';
import './App.css';
// import { message } from 'antd';
import { Previews } from './dropzone';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} style={{
          position: 'relative',
          top: '-30px'
        }} className="App-logo" alt="logo" />
        <Previews />
      </header>
    </div>
  );
}

export default App;
