import React, {useEffect, useState} from 'react';
import {useDropzone} from 'react-dropzone';

const thumbsContainer = {
  display: 'flex',
  flexDirection: 'row',
  flexWrap: 'wrap',
  marginTop: 16
};

const thumb = {
  display: 'inline-flex',
  borderRadius: 2,
  border: '1px solid #eaeaea',
  marginBottom: 8,
  marginRight: 8,
  width: 100,
  height: 100,
  padding: 4,
  boxSizing: 'border-box'
};

const thumbInner = {
  display: 'flex',
  minWidth: 0,
  overflow: 'hidden'
};

const img = {
  display: 'block',
  width: 'auto',
  height: '100%'
};


export function Previews(props) {
  const [files, setFiles] = useState([]);
  const [display, setDisplay] = useState();
  const {getRootProps, getInputProps} = useDropzone({
    accept: 'image/*',
    onDrop: acceptedFiles => {
      setFiles(acceptedFiles.map(file => Object.assign(file, {
        preview: URL.createObjectURL(file)
      })));
    }
  });
  
  const thumbs = files.map(file => (
    <div style={thumb} key={file.name}>
      <div style={thumbInner}>
        <img
          alt={"tt"}
          src={file.preview}
          style={img}
        />
      </div>
    </div>
  ));

  useEffect(() => {
    // Make sure to revoke the data uris to avoid memory leaks
    files.forEach(file => URL.revokeObjectURL(file.preview));
  }, [files]);

  useEffect(() => {
    console.log(display)
  }, [display]);

  const uploadFiles = () => {
    let formData = new FormData();

    for (var i = 0; i < files.length; i++) {
        let file = files[i];
        formData.append('articleFiles[]', file);
    }
    
    fetch("https://uoft-taco.herokuapp.com/detector/", {
      method: 'POST',
      mode: 'cors',
      body: formData
    }).then(response => response.blob()).then((myBlob) => {
      setDisplay(URL.createObjectURL(myBlob))
    })
  }
  
  return (
    <section style={{
        backgroundColor: "#ff000059",
        paddingLeft: "15px",
        paddingRight: "15px",
    }} className="container">
      <div style={{
        cursor: "pointer",
        backgroundColor: "#ff880042",
        paddingLeft: 120,
        paddingRight: 120
      }} {...getRootProps({className: 'dropzone'})}>
        <input {...getInputProps()} />
        <p>Click here to select files</p>
      </div>
      <aside style={thumbsContainer}>
        {thumbs}
      </aside>
      <div style={{paddingBottom: "10px"}}>
        {files.length > 0 && 
          <React.Fragment>
            <button onClick={uploadFiles}>Submit</button>
          </React.Fragment>}
      </div>
      {display ? <img alt='dasd' src={display}></img>: <></>}

    </section>
  );
}