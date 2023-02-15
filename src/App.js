import React from "react";
import { legacy_createStore as createStore, combineReducers, applyMiddleware } from "redux";
import { taskMiddleware } from "react-palm/tasks";
import { Provider } from "react-redux";
import KeplerGl from "kepler.gl";
import keplerGlReducer from "kepler.gl/reducers";

const reducers = combineReducers({keplerGl: keplerGlReducer});
const store = createStore(reducers, {}, applyMiddleware(taskMiddleware));
const mapboxAccessToken = "";

function App() {
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
        mapboxApiAccessToken = {mapboxAccessToken}
        width={window.innerWidth}
        height={window.innerHeight}/>
}

export default App;
