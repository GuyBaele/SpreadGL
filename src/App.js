import React, {useEffect, useState} from "react";
import { legacy_createStore as createStore, combineReducers, applyMiddleware } from "redux";
import { taskMiddleware } from "react-palm/tasks";
import { Provider } from "react-redux";
import KeplerGl from "kepler.gl";
import keplerGlReducer from "kepler.gl/reducers";
import {token} from "./mapbox";


const reducers = combineReducers({
  keplerGl: keplerGlReducer
});

const store = createStore(reducers, {}, applyMiddleware(taskMiddleware));

function App() {
    // var [mapboxAccessToken, setToken] = useState("");
    //
    // useEffect(()=>{
    //     getToken();
    //     console.log(mapboxAccessToken);
    // },[mapboxAccessToken]);
    //
    // async function getToken() {
    //     try{
    //         const res = await fetch(raw)
    //         const data = await res.text();
    //         setToken(data);
    //     } catch (err){
    //         console.error(err);
    //     }
      return (
          <div className="App">
                <Provider store={store}>
                    <Map/>
                </Provider>
          </div>
      );
}

function Map() {
    return <KeplerGl
        id="SpreadGL"
        mapboxApiAccessToken = {token}
        width={window.innerWidth}
        height={window.innerHeight}/>
}

export default App;
