// SPDX-License-Identifier: MIT
// Copyright contributors to the kepler.gl project

import {LoadDataModalFactory, withState} from '@kepler.gl/components';
import {LOADING_METHODS} from '../constants/default-settings';

import SampleMapGallery from '../components/load-data-modal/sample-data-viewer';
import LoadRemoteMap from '../components/load-data-modal/load-remote-map';
import SampleMapsTab from '../components/load-data-modal/sample-maps-tab';
import {loadRemoteMap, loadSample, loadSampleConfigurations} from '../actions';

const CustomLoadDataModalFactory = (...deps) => {
  const LoadDataModal = LoadDataModalFactory(...deps);
  
  // FIX: Destructure dependencies to get the original components.
  // Kepler's LoadDataModalFactory dependencies are: [ModalDialog, UploadFile, LoadStorageMap]
  // We need UploadFile (index 1) and LoadStorageMap (index 2) to recreate the default methods.
  const UploadFile = deps[1];
  const LoadStorageMap = deps[2];

  // FIX: Manually reconstruct default methods instead of reading from defaultProps (which is undefined in v3)
  const defaultLoadingMethods = [
    {
      id: LOADING_METHODS.upload || 'upload',
      label: 'modal.loadData.upload',
      elementType: UploadFile
    },
    {
      id: LOADING_METHODS.storage || 'storage',
      label: 'modal.loadData.storage',
      elementType: LoadStorageMap
    }
  ];

  const additionalMethods = {
    remote: {
      id: LOADING_METHODS.remote,
      label: 'modal.loadData.remote',
      elementType: LoadRemoteMap
    },
    sample: {
      id: LOADING_METHODS.sample,
      label: 'modal.loadData.sample',
      elementType: SampleMapGallery,
      tabElementType: SampleMapsTab
    }
  };

  // add more loading methods
  // FIX: Safely assign defaultProps using "|| {}" to handle the undefined case
  LoadDataModal.defaultProps = {
    ...(LoadDataModal.defaultProps || {}),
    loadingMethods: [
      defaultLoadingMethods.find(lm => lm.id === 'upload'),
      additionalMethods.remote,
      defaultLoadingMethods.find(lm => lm.id === 'storage'),
      additionalMethods.sample
    ]
  };

  return withState([], state => ({...state.demo.app, ...state.demo.keplerGl.map.uiState}), {
    onLoadSample: loadSample,
    onLoadRemoteMap: loadRemoteMap,
    loadSampleConfigurations
  })(LoadDataModal);
};

CustomLoadDataModalFactory.deps = LoadDataModalFactory.deps;

export function replaceLoadDataModal() {
  return [LoadDataModalFactory, CustomLoadDataModalFactory];
}