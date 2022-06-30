import React from "react";
import { createStore, combineReducers, applyMiddleware } from "redux";
import { taskMiddleware } from "react-palm/tasks";
import { Provider } from "react-redux";
import KeplerGl from "kepler.gl";
import keplerGlReducer from "kepler.gl/reducers";
// import { addDataToMap } from "kepler.gl/actions";
// import useSWR from "swr";, useDispatch

window.process = {
  env: {
      NODE_ENV: 'test'
  }
}

const reducers = combineReducers({
  keplerGl: keplerGlReducer
});

const store = createStore(reducers, {}, applyMiddleware(taskMiddleware));

function App() {
  return (
    <Provider store={store}>
      <Map />
    </Provider>
  );
}

function Map() {
  
  // const dispatch = useDispatch();
  // const fetcher = (url) => fetch(url).then((res) => res.json());
  // const { data } = useSWR(
  //   "https://gist.githubusercontent.com/FlorentLee/25f29315b1973b09adac3c062f521858/raw/22d970452089192f6ca3cb637387b6b58f522bb9/data.json",
  //   fetcher);
  //
  // React.useEffect(() => {
  //   if (data) {
  //     dispatch(
  //       addDataToMap({
  //         datasets: {
  //           info: {
  //             label: "Omicron Cases in Belgium",
  //             id: "omicron_belgium"
  //           },
  //           data
  //         },
  //         option: {
  //           centerMap: true,
  //           readOnly: false
  //         },
  //         config: {
  //           mapStyle: {styleType: 'dark'}
  //         }
  //       })
  //     );
  //   }
  // }, [dispatch, data]);

  return (
    <KeplerGl
      id="SpreadGL"
      mapboxApiAccessToken = "pk.eyJ1IjoiZGFqYXAiLCJhIjoiY2t6bzhyYzY5NGxuYTJubzF2anNzNjBxdiJ9.OQ8pxr8aRxtFSmlPg8NOvg"
      width={window.innerWidth}
      height={window.innerHeight}
    />
  );
}

export default App;