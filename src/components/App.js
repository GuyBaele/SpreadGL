import React from "react";
import { legacy_createStore as createStore, combineReducers, applyMiddleware } from "redux";
import { taskMiddleware } from "react-palm/tasks";
import { Provider } from "react-redux";
import KeplerGl from "kepler.gl";
import keplerGlReducer from "kepler.gl/reducers";
import AutoSizer from "react-virtualized/dist/commonjs/AutoSizer";

const reducers = combineReducers({keplerGl: keplerGlReducer});
const store = createStore(reducers, {}, applyMiddleware(taskMiddleware));
const mapboxAccessToken = "pk.eyJ1IjoiZGFqYXAiLCJhIjoiY2xhaWRhbHFzMDFkOTN1cGp1N2xxOXV2ZyJ9.paHEbrE0krDorE3WWqiUAg";

function App() {
      return (
          <div className="App">
                <div style={{ display: 'flex' }}>
                    <div style={{flex: '1 1 auto'}}>
                        <AutoSizer>{() => (
                            <Provider store={store}>
                                <Map/>
                            </Provider>)}
                        </AutoSizer>
                    </div>
                </div>
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
