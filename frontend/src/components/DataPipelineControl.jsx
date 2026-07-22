import React, { useState, useRef, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';
import { addDataToMap, addNotification } from '@kepler.gl/actions';
import { processGeojson, processCsvData } from '@kepler.gl/processors';
import KeplerGlSchema from '@kepler.gl/schemas';

const SPREADGL_DEFAULT_CONFIG = {
  version: 'v1',
  config: {
    mapState: {
      latitude: 35.0,
      longitude: 105.0,
      zoom: 3.8
    },
    visState: {
      layers: [
        {
          id: 'dynamic_pathway_trip',
          type: 'trip',
          config: {
            dataId: 'dynamic_pathway',
            label: 'Dynamic Pathway',
            isVisible: true,
            columns: {
              geojson: '_geojson'
            },
            visConfig: {
              opacity: 0.8,
              thickness: 2.0,
              trailLength: 180
            }
          }
        },
        {
          id: 'hpd_polygons_geojson',
          type: 'geojson',
          config: {
            dataId: 'hpd_polygons',
            label: 'HPD Polygons',
            isVisible: true,
            columns: {
              geojson: '_geojson'
            },
            visConfig: {
              opacity: 0.2,
              filled: true,
              stroked: false,
              colorRange: {
                name: 'Colorblind Friendly',
                type: 'sequential',
                category: 'Custom',
                colors: ['#D6DEBF', '#95C590', '#58A690', '#49828A', '#415F79', '#383C65']
              }
            },
            visualChannels: {
              colorField: {
                name: 'hpd_level',
                type: 'integer'
              },
              colorScale: 'quantile'
            }
          }
        },
        {
          id: 'aggregated_migration_network_arc',
          type: 'arc',
          config: {
            dataId: 'aggregated_migration_network',
            label: 'Aggregated Migration Network',
            isVisible: true,
            color: [18, 147, 154],
            columns: {
              lat0: 'start_lat',
              lng0: 'start_lon',
              lat1: 'end_lat',
              lng1: 'end_lon'
            },
            visConfig: {
              targetColor: [224, 58, 62],
              opacity: 0.8,
              strokeWidthRange: [0, 10]
            },
            visualChannels: {
              sizeField: {
                name: 'jump_weight',
                type: 'integer'
              },
              sizeScale: 'linear'
            }
          }
        }
      ]
    }
  }
};

// --- STYLED COMPONENTS & ANIMATIONS ---

const pulseGlow = keyframes`
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 15px rgba(203, 185, 68, 0.35);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 25px rgba(203, 185, 68, 0.6);
    opacity: 1;
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 15px rgba(203, 185, 68, 0.35);
    opacity: 0.8;
  }
`;

const rotateBg = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const PanelContainer = styled.div`
  width: 100%;
  background: #ffffff;
  border: 1px solid rgba(16, 107, 163, 0.18);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  color: #2D3748;
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  overflow: hidden;
  box-sizing: border-box;
  margin: 0 auto;
`;

const EnvToggleGroup = styled.div`
  display: flex;
  background: #f0f4f8;
  border-radius: 8px;
  padding: 3px;
  margin-top: 10px;
  margin-bottom: 16px;
  border: 1px solid rgba(16, 107, 163, 0.25);
`;

const EnvToggleBtn = styled.button`
  flex: 1;
  background: ${props => props.$active ? 'linear-gradient(135deg, #106ba3 0%, #1e88e5 100%)' : 'transparent'};
  border: none;
  color: ${props => props.$active ? '#ffffff' : '#475569'};
  padding: 10px;
  font-size: 13px;
  font-weight: 700;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Outfit', sans-serif;

  &:hover {
    color: ${props => props.$active ? '#ffffff' : '#106ba3'};
  }
`;

const LocationMismatchAlert = styled.div`
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.4);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
`;

const AlertHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  color: #ef4444;
  font-weight: 700;
  font-size: 15px;
  margin-bottom: 8px;
`;

const LocationList = styled.div`
  background: #fef2f2;
  border: 1px solid #fca5a5;
  border-radius: 8px;
  padding: 14px;
  margin-top: 10px;
  font-family: monospace;
  font-size: 13px;
  color: #b91c1c;
  max-height: 150px;
  overflow-y: auto;
  line-height: 1.6;
`;

const CollapsedTrigger = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  cursor: pointer;
  background: transparent;
  animation: ${pulseGlow} 2s infinite ease-in-out;
  border-radius: 50%;
  border: 1px solid rgba(203, 185, 68, 0.5);
`;

const PanelHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px;
  background: #f8fafc;
  border-bottom: 1px solid rgba(16, 107, 163, 0.25);
`;

const Title = styled.h3`
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  font-family: 'Outfit', sans-serif;
  color: #106ba3;
`;

const CloseButton = styled.button`
  background: transparent;
  border: none;
  color: #a0aec0;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;

  &:hover {
    color: #ff4f4f;
  }
`;

// --- STEP INDICATOR ---

const StepsWrapper = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px;
  background: #f8fafc;
  border-bottom: 1px solid rgba(16, 107, 163, 0.15);
`;

const StepItem = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;

  &:not(:last-child)::after {
    content: '';
    position: absolute;
    top: 13px;
    left: calc(50% + 18px);
    right: calc(-50% + 18px);
    height: 2.5px;
    background: ${props => props.$completed ? '#106ba3' : 'rgba(16, 107, 163, 0.15)'};
    z-index: 1;
    transition: background 0.3s ease;
  }
`;

const StepBubble = styled.div`
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: ${props => props.$active ? '#C89B3C' : props.$completed ? '#106ba3' : 'rgba(16, 107, 163, 0.12)'};
  color: ${props => props.$active ? '#ffffff' : props.$completed ? '#ffffff' : '#94a3b8'};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  z-index: 2;
  box-shadow: ${props => props.$active ? '0 0 12px rgba(200, 155, 60, 0.45)' : 'none'};
  transition: all 0.3s ease;
  font-family: 'Outfit', sans-serif;
`;

const StepLabel = styled.div`
  font-size: 11px;
  color: ${props => props.$active ? '#C89B3C' : props.$completed ? '#106ba3' : '#94a3b8'};
  margin-top: 6px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-family: 'Outfit', sans-serif;
`;

// --- FORM STYLES ---

const ScrollableContent = styled.div`
  flex: 1;
  padding: 24px;
  box-sizing: border-box;
`;

const ToggleGroup = styled.div`
  display: flex;
  background: #f0f4f8;
  border-radius: 8px;
  padding: 3px;
  margin-bottom: 16px;
  border: 1px solid rgba(16, 107, 163, 0.2);
`;

const ToggleBtn = styled.button`
  flex: 1;
  background: ${props => props.$active ? 'linear-gradient(135deg, #106ba3 0%, #1e88e5 100%)' : 'transparent'};
  border: none;
  color: ${props => props.$active ? '#ffffff' : '#475569'};
  padding: 10px;
  font-size: 13px;
  font-weight: 700;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Outfit', sans-serif;

  &:hover {
    color: ${props => props.$active ? '#ffffff' : '#106ba3'};
  }
`;

const FileInputWrapper = styled.div`
  margin-bottom: 12px;
`;

const Label = styled.label`
  display: block;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #106ba3;
  margin-bottom: 6px;
  font-weight: 700;
`;

const HiddenInput = styled.input`
  display: none;
`;

const FileUploadBtn = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f8fafc;
  border: 1.5px dashed ${props => props.$hasFile ? '#C89B3C' : 'rgba(16, 107, 163, 0.35)'};
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  color: ${props => props.$hasFile ? '#C89B3C' : '#475569'};

  &:hover {
    border-color: #106ba3;
    background: #f1f5f9;
  }
`;

const RemoveBtn = styled.button`
  background: transparent;
  border: none;
  color: #a0aec0;
  cursor: pointer;
  padding: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  
  &:hover {
    color: #ff4f4f;
    background: rgba(255, 79, 79, 0.1);
  }
`;

const InputGroup = styled.div`
  margin-bottom: 12px;
`;

const TextInput = styled.input`
  width: 100%;
  padding: 10px 14px;
  background: #ffffff;
  border: 1.5px solid rgba(16, 107, 163, 0.35);
  border-radius: 10px;
  color: #2D3748;
  font-size: 15px;
  transition: all 0.2s ease;
  box-sizing: border-box;
  font-family: 'Inter', sans-serif;

  &:focus {
    outline: none;
    border-color: #106ba3;
    box-shadow: 0 0 8px rgba(16, 107, 163, 0.25);
  }

  &:disabled {
    background: #f1f5f9;
    color: #94a3b8;
    border-color: #cbd5e1;
    cursor: not-allowed;
  }
`;

const SliderGroup = styled.div`
  margin-bottom: 14px;
`;

const SliderHeader = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #106ba3;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-weight: 700;
`;

const SliderInput = styled.input`
  width: 100%;
  accent-color: #C89B3C;
  cursor: pointer;
  background: #e2e8f0;
  height: 6px;
  border-radius: 3px;
  outline: none;
  
  &:disabled {
    cursor: not-allowed;
    accent-color: #e2e8f0;
  }
`;

// --- ACCORDION ---

const Accordion = styled.div`
  margin-top: 16px;
  border-top: 1px solid rgba(104, 163, 187, 0.12);
`;

const AccordionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  cursor: pointer;
  color: #106ba3;
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  user-select: none;
  font-family: 'Outfit', sans-serif;

  &:hover {
    color: #1e88e5;
  }
`;

const AccordionContent = styled.div`
  max-height: ${props => props.$isOpen ? '1000px' : '0'};
  opacity: ${props => props.$isOpen ? '1' : '0'};
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
`;

const CheckboxContainer = styled.label`
  display: flex;
  align-items: center;
  margin-top: 10px;
  margin-bottom: 12px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  user-select: none;
  font-family: 'Inter', sans-serif;
  
  &:hover {
    color: #106ba3;
  }
`;

const CheckboxInput = styled.input`
  margin-right: 8px;
  accent-color: #106ba3;
`;

const SubSection = styled.div`
  background: #f8fafc;
  border-left: 3px solid #106ba3;
  padding: 16px 20px 6px 20px;
  border-radius: 0 12px 12px 0;
  margin-bottom: 16px;
  border-top: 1px solid rgba(16, 107, 163, 0.08);
  border-right: 1px solid rgba(16, 107, 163, 0.08);
  border-bottom: 1px solid rgba(16, 107, 163, 0.08);
`;

const HelpText = styled.div`
  font-size: 11.5px;
  color: #64748b;
  margin-top: 4px;
  line-height: 1.4;
  font-family: 'Inter', sans-serif;
`;

// --- BUTTONS ---

const SubmitButton = styled.button`
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #106ba3 0%, #1e88e5 100%);
  border: none;
  border-radius: 10px;
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(16, 107, 163, 0.25);
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: 'Outfit', sans-serif;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(16, 107, 163, 0.45);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    background: #cbd5e1;
    color: #94a3b8;
    box-shadow: none;
    cursor: not-allowed;
  }
`;

const SecondaryButton = styled.button`
  width: 100%;
  padding: 12px;
  background: transparent;
  border: 1.5px solid rgba(16, 107, 163, 0.3);
  border-radius: 10px;
  color: #106ba3;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 8px;
  font-family: 'Outfit', sans-serif;

  &:hover {
    color: #106ba3;
    border-color: #106ba3;
    background: rgba(16, 107, 163, 0.05);
  }
`;

// --- STAGING PANEL ---

const FileList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
`;

const FileCard = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8fafc;
  border: 1.5px solid rgba(16, 107, 163, 0.18);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(16, 107, 163, 0.03);

  @media (max-width: 600px) {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
`;

const FileCardLeft = styled.div`
  display: flex;
  flex-direction: column;
  max-width: 70%;

  @media (max-width: 600px) {
    max-width: 100%;
  }
`;

const FileName = styled.div`
  font-size: 15px;
  font-weight: 700;
  color: #2D3748;
  font-family: 'Outfit', sans-serif;
`;

const FileDetails = styled.div`
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
`;

const DownloadBtn = styled.button`
  background: transparent;
  border: 1.5px solid #106ba3;
  color: #106ba3;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Outfit', sans-serif;

  &:hover {
    background: rgba(16, 107, 163, 0.08);
    box-shadow: 0 0 8px rgba(16, 107, 163, 0.2);
  }
`;

const ErrorCard = styled.div`
  background: rgba(255, 75, 75, 0.08);
  border: 1px solid rgba(255, 75, 75, 0.25);
  border-radius: 8px;
  padding: 14px;
  color: #ff4f4f;
  font-size: 12px;
  line-height: 1.5;
  margin-bottom: 20px;
`;

const Spinner = styled.div`
  width: 44px;
  height: 44px;
  border: 3px solid rgba(104, 163, 187, 0.15);
  border-radius: 50%;
  border-top-color: #68A3BB;
  animation: ${rotateBg} 1s linear infinite;
  margin: 30px auto 16px auto;
  box-shadow: 0 0 15px rgba(104, 163, 187, 0.25);
`;

const StatusText = styled.div`
  text-align: center;
  font-size: 13px;
  color: #a0aec0;
  margin-bottom: 24px;
  font-weight: 500;
`;

const DirectUploadCard = styled.div`
  background: #f8fafc;
  border: 1.5px dashed rgba(16, 107, 163, 0.25);
  border-radius: 12px;
  padding: 24px 20px;
  margin-bottom: 24px;
  text-align: center;
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    border-color: #1e88e5;
    background: rgba(16, 107, 163, 0.04);
  }
`;

// --- RENDER VISUALIZATION ---

const VizActiveCard = styled.div`
  text-align: center;
  padding: 24px 16px;
  background: rgba(104, 163, 187, 0.03);
  border: 1px dashed rgba(104, 163, 187, 0.3);
  border-radius: 12px;
  margin-bottom: 20px;
`;

const RadarContainer = styled.div`
  position: relative;
  width: 60px;
  height: 60px;
  margin: 0 auto 16px auto;
`;

const RadarCircle = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid #CBB944;
  animation: ${pulseGlow} 2s infinite ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const VizTitle = styled.div`
  font-size: 15px;
  font-weight: 700;
  color: #CBB944;
  margin-bottom: 6px;
`;

const VizDesc = styled.div`
  font-size: 12px;
  color: #a0aec0;
  line-height: 1.4;
`;

// --- HELPER COMPONENT: FILE INPUT ---

const FileInput = ({ label, accept, file, onChange, required, multiple, directory }) => {
  const fileInputRef = useRef(null);

  const handleClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      let filesList = Array.from(e.target.files);
      if (directory) {
        if (accept) {
          const extensions = accept.split(',').map(ext => ext.trim().toLowerCase());
          filesList = filesList.filter(f => {
            const name = f.name.toLowerCase();
            return extensions.some(ext => name.endsWith(ext));
          });
        }
        onChange(filesList);
      } else if (multiple) {
        onChange(filesList);
      } else {
        onChange(e.target.files[0]);
      }
    }
  };

  const handleRemove = (e) => {
    e.stopPropagation();
    onChange(multiple || directory ? [] : null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const renderFileName = () => {
    if (directory) {
      if (file && file.length > 0) {
        const path = file[0].webkitRelativePath;
        const folderName = path ? path.split('/')[0] : '';
        return `Folder "${folderName}" (${file.length} TIFF files selected)`;
      }
      return 'Select TIFFs directory...';
    }
    if (multiple) {
      if (file && file.length > 0) {
        return `${file.length} file(s) selected: ${file.map(f => f.name).join(', ')}`;
      }
      return 'Choose files...';
    }
    return file ? file.name : 'Choose file...';
  };

  const hasFile = (multiple || directory) ? (file && file.length > 0) : !!file;

  return (
    <FileInputWrapper>
      <Label>
        {label} {required && <span style={{ color: '#ff4f4f' }}>*</span>}
      </Label>
      <HiddenInput 
        type="file" 
        accept={accept} 
        ref={fileInputRef} 
        onChange={handleFileChange}
        multiple={multiple}
        {...(directory ? { webkitdirectory: "true", directory: "true" } : {})}
      />
      <FileUploadBtn $hasFile={hasFile} onClick={handleClick}>
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '85%' }}>
          {renderFileName()}
        </span>
        {hasFile ? (
          <RemoveBtn onClick={handleRemove}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </RemoveBtn>
        ) : (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
        )}
      </FileUploadBtn>
    </FileInputWrapper>
  );
};

// --- MAIN PIPELINE CONTROL COMPONENT ---

export default function DataPipelineControl({ dispatch, activeTab, setActiveTab, userMapboxToken = '', setUserMapboxToken, enableTianditu = false, setEnableTianditu, onResultsChange }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [visualized, setVisualized] = useState(false);

  const directInputRef = useRef(null);

  const handleDirectUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const fileContent = event.target.result;
        const lowerName = file.name.toLowerCase();
        const dataId = file.name.replace(/\.[^/.]+$/, "");

        if (lowerName.endsWith('.geojson') || lowerName.endsWith('.json')) {
          const parsedJson = JSON.parse(fileContent);
          
          if (parsedJson.datasets && parsedJson.config) {
            // 1. Unpack the serialized Kepler map state
            const loadedMap = KeplerGlSchema.load(
              parsedJson.datasets,
              parsedJson.config
            );
            // 2. Dispatch the unpacked state
            dispatch(addDataToMap(loadedMap));
            setLoading(false);
            setActiveTab('render');
            return;
          }
          
          const processedData = processGeojson(parsedJson);
          dispatch(addDataToMap({
            datasets: [{ info: { id: dataId, label: file.name }, data: processedData }],
            options: { keepExistingConfig: true }
          }));
        } else if (lowerName.endsWith('.csv')) {
          const processedData = processCsvData(fileContent);
          dispatch(addDataToMap({
            datasets: [{
              info: {
                id: dataId,
                label: file.name
              },
              data: processedData
            }],
            options: {
              keepExistingConfig: true
            },
            config: SPREADGL_DEFAULT_CONFIG
          }));
        } else {
          setError('Unsupported file format. Please upload .geojson, .json, or .csv.');
          setLoading(false);
          return;
        }

        setLoading(false);
        setActiveTab('render');
      } catch (err) {
        setError(`Failed to parse file: ${err.message}`);
        setLoading(false);
      }
    };

    reader.onerror = () => {
      setError('Error reading file.');
      setLoading(false);
    };

    reader.readAsText(file);
  };

  // Form states
  const [analysisType, setAnalysisType] = useState('discrete');
  const [treeFile, setTreeFile] = useState(null);
  const [locationFile, setLocationFile] = useState(null);
  const [logFile, setLogFile] = useState(null);

  const [mostRecentTip, setMostRecentTip] = useState('');
  const [dateFormat, setDateFormat] = useState('YYYY-MM-DD');
  const [locationTrait, setLocationTrait] = useState('');
  const [bfThreshold, setBfThreshold] = useState(3.0);
  const [burnin, setBurnin] = useState(0.1);

  // Environmental States
  const [envType, setEnvType] = useState('none'); // 'none' | 'regions' | 'raster'

  // Regions states
  const [envRegionsMap, setEnvRegionsMap] = useState(null);
  const [envRegionsData, setEnvRegionsData] = useState(null);
  const [envRegionsLocCol, setEnvRegionsLocCol] = useState('');
  const [envRegionsLocVar, setEnvRegionsLocVar] = useState('');

  // Raster states
  const [envRasterMap, setEnvRasterMap] = useState(null);
  const [envRasterTiffFiles, setEnvRasterTiffFiles] = useState([]);
  const [envRasterLocVar, setEnvRasterLocVar] = useState('');
  const [envRasterLocList, setEnvRasterLocList] = useState(null);
  const [envRasterMode, setEnvRasterMode] = useState('static'); // 'static' | 'dynamic'

  // Advanced States
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
  const [reproject, setReproject] = useState(false);
  const [reprojectSource, setReprojectSource] = useState('');
  const [reprojectTarget, setReprojectTarget] = useState('');
  const [reprojectLat, setReprojectLat] = useState('');
  const [reprojectLon, setReprojectLon] = useState('');

  const [trim, setTrim] = useState(false);
  const [referencedFile, setReferencedFile] = useState(null);
  const [trimPrimaryKey, setTrimPrimaryKey] = useState('');
  const [trimForeignKey, setTrimForeignKey] = useState('');
  const [trimNullQueries, setTrimNullQueries] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!treeFile) {
      setError('Tree file (.trees) is required.');
      return;
    }
    if (analysisType === 'discrete' && !locationFile) {
      setError('Location list (.csv) is required for Discrete analysis.');
      return;
    }
    if (!mostRecentTip) {
      setError('Most Recent Tip parameter is required.');
      return;
    }
    if (!locationTrait) {
      setError('Location Trait parameter is required.');
      return;
    }

    // Environmental validation
    if (envType === 'regions') {
      if (!envRegionsMap || !envRegionsData || !envRegionsLocCol || !envRegionsLocVar) {
        setError('All Regional Polygons fields are required.');
        return;
      }
    } else if (envType === 'raster') {
      if (!envRasterMap || envRasterTiffFiles.length === 0 || !envRasterLocVar || !envRasterLocList) {
        setError('All Environmental Rasters fields are required.');
        return;
      }
    }

    setLoading(true);
    setError(null);
    setResults(null);
    setVisualized(false);
    setActiveTab('staging');

    const formData = new FormData();
    formData.append('analysis_type', analysisType);
    formData.append('most_recent_tip', mostRecentTip);
    formData.append('location_trait', locationTrait);
    formData.append('date_format', dateFormat);
    formData.append('bf_threshold', bfThreshold);
    formData.append('burnin', burnin);
    formData.append('tree_file', treeFile);

    if (logFile) {
      formData.append('log_file', logFile);
    }
    if (locationFile) {
      formData.append('location_file', locationFile);
    }

    formData.append('reproject', reproject);
    if (reproject) {
      formData.append('reproject_source', reprojectSource);
      formData.append('reproject_target', reprojectTarget);
      formData.append('reproject_lat', reprojectLat);
      formData.append('reproject_lon', reprojectLon);
    }

    formData.append('trim', trim);
    if (trim) {
      if (referencedFile) {
        formData.append('referenced_file', referencedFile);
      }
      formData.append('trim_primary_key', trimPrimaryKey);
      formData.append('trim_foreign_key', trimForeignKey);
      formData.append('trim_null_queries', trimNullQueries);
    }

    formData.append('env_type', envType);
    if (envType === 'regions') {
      formData.append('env_regions_map', envRegionsMap);
      formData.append('env_regions_data', envRegionsData);
      formData.append('env_regions_loc_col', envRegionsLocCol);
      formData.append('env_regions_loc_var', envRegionsLocVar);
    } else if (envType === 'raster') {
      formData.append('env_raster_map', envRasterMap);
      formData.append('env_raster_loc_var', envRasterLocVar);
      formData.append('env_raster_loc_list', envRasterLocList);
      formData.append('env_raster_mode', envRasterMode);
      envRasterTiffFiles.forEach((file) => {
        formData.append('env_raster_tiff_files', file);
      });
    }

    try {
      const apiUrl = (process.env.BACKEND_API_URL || 'http://localhost:8000').replace(/\/$/, '');
      const response = await fetch(`${apiUrl}/api/process-tree`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errText = await response.text();
        let parsedErr;
        try {
          parsedErr = JSON.parse(errText);
        } catch (errParse) {}
        throw new Error(parsedErr?.detail || parsedErr?.message || `API Error (${response.status})`);
      }

      const data = await response.json();
      setResults(data);
      setLoading(false);
    } catch (err) {
      setError(err.message || 'An error occurred during Backend processing.');
      setLoading(false);
    }
  };

  const handleDownload = (filename, dataObj, isCsv) => {
    let blob;
    if (isCsv) {
      if (Array.isArray(dataObj) && dataObj.length > 0) {
        const headers = Object.keys(dataObj[0]);
        const csvRows = [
          headers.join(','),
          ...dataObj.map(row => 
            headers.map(fieldName => {
              const val = row[fieldName];
              if (typeof val === 'string' && (val.includes(',') || val.includes('"') || val.includes('\n'))) {
                return `"${val.replace(/"/g, '""')}"`;
              }
              return val ?? '';
            }).join(',')
          )
        ];
        blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
      } else {
        blob = new Blob([dataObj], { type: 'text/plain' });
      }
    } else {
      blob = new Blob([JSON.stringify(dataObj, null, 2)], { type: 'application/json' });
    }
    const href = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = href;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(href);
  };

  const handleVisualize = () => {
    if (!results) return;

    const parseGeoJson = (data) => (typeof data === 'string' ? JSON.parse(data) : data);

    const parsedPathway = results.dynamic_pathway ? parseGeoJson(results.dynamic_pathway) : null;
    const parsedHpd = results.hpd_polygons ? parseGeoJson(results.hpd_polygons) : null;
    const parsedNetwork = results.aggregated_migration_network ? parseGeoJson(results.aggregated_migration_network) : null;

    let trailLength = 180;
    if (parsedPathway && parsedPathway.features) {
      let minTs = Infinity;
      let maxTs = -Infinity;
      const processCoord = (coord) => {
        if (Array.isArray(coord) && coord.length >= 4) {
          const ts = coord[3];
          if (typeof ts === 'number' && !isNaN(ts)) {
            if (ts < minTs) minTs = ts;
            if (ts > maxTs) maxTs = ts;
          }
        }
      };
      parsedPathway.features.forEach(feature => {
        if (feature.geometry && feature.geometry.coordinates) {
          const coords = feature.geometry.coordinates;
          if (Array.isArray(coords)) {
            if (Array.isArray(coords[0]) && typeof coords[0][0] === 'number') {
              coords.forEach(processCoord);
            } else if (Array.isArray(coords[0]) && Array.isArray(coords[0][0])) {
              coords.forEach(subCoords => {
                if (Array.isArray(subCoords)) {
                  subCoords.forEach(processCoord);
                }
              });
            }
          }
        }
      });
      if (minTs !== Infinity && maxTs !== -Infinity && maxTs > minTs) {
        trailLength = (maxTs - minTs) * 0.1;
      }
    }

    let geoContextualDataset = null;
    if (results.geo_contextual_data) {
      if (results.geo_contextual_type === 'geojson') {
        const parsedGeoContextual = parseGeoJson(results.geo_contextual_data);
        geoContextualDataset = {
          info: { label: 'Geo-Contextual Data (GeoJSON)', id: 'geo_contextual_data', format: 'geojson' },
          data: processGeojson(parsedGeoContextual)
        };
      } else if (results.geo_contextual_type === 'csv') {
        const data = results.geo_contextual_data;
        if (Array.isArray(data) && data.length > 0) {
          const headers = Object.keys(data[0]);
          const csvString = [
            headers.join(','),
            ...data.map(row => 
              headers.map(fieldName => {
                const val = row[fieldName];
                if (typeof val === 'string' && (val.includes(',') || val.includes('"') || val.includes('\n'))) {
                  return `"${val.replace(/"/g, '""')}"`;
                }
                return val ?? '';
              }).join(',')
            )
          ].join('\n');
          
          geoContextualDataset = {
            info: { label: 'Geo-Contextual Data (CSV)', id: 'geo_contextual_data', format: 'csv' },
            data: processCsvData(csvString)
          };
        }
      }
    }

    let datasets = [];

    if (parsedPathway) {
      datasets.push({
        info: { label: 'Dynamic Pathway', id: 'dynamic_pathway', format: 'geojson' },
        data: processGeojson(parsedPathway)
      });
    }

    if (analysisType === 'continuous' && parsedHpd && parsedHpd.features && parsedHpd.features.length > 0) {
      datasets.push({
        info: { label: 'HPD Polygons', id: 'hpd_polygons', format: 'geojson' },
        data: processGeojson(parsedHpd)
      });
    }

    if (analysisType === 'discrete' && parsedNetwork) {
      datasets.push({
        info: { label: 'Aggregated Migration Network', id: 'aggregated_migration_network', format: 'geojson' },
        data: processGeojson(parsedNetwork)
      });
    }

    if (geoContextualDataset) {
      datasets.push(geoContextualDataset);
    }

    const mapStyleConfig = {
      styleType: 'carto_positron',
      visibleLayerGroups: {
        water: true,
        border: true,
        label: true
      },
      topLayerGroups: {
        label: true
      }
    };

    const dynamicPathwayLayer = {
      id: 'dynamic_pathway_trip',
      type: 'trip',
      config: {
        dataId: 'dynamic_pathway',
        label: 'Dynamic Pathway',
        isVisible: true,
        columns: {
          geojson: '_geojson'
        },
        visConfig: {
          opacity: 0.8,
          thickness: 2.0,
          trailLength: trailLength
        }
      }
    };

    const aggregatedMigrationNetworkLayer = {
      id: 'aggregated_network_layer',
      type: 'arc',
      config: {
        dataId: 'aggregated_migration_network',
        label: 'Aggregated Migration Network',
        isVisible: false,
        color: [255, 153, 31],
        columns: {
          lat0: 'start_lat',
          lng0: 'start_lon',
          lat1: 'end_lat',
          lng1: 'end_lon'
        },
        visConfig: {
          opacity: 0.8,
          thickness: 2,
          sizeRange: [0, 10],
          targetColor: [255, 153, 31]
        },
        visualChannels: {
          sizeField: {
            name: 'jump_weight',
            type: 'integer'
          },
          sizeScale: 'linear'
        }
      },
      visualChannels: {
        sizeField: {
          name: 'jump_weight',
          type: 'integer'
        },
        sizeScale: 'linear'
      }
    };

    let geoContextualLayer = null;
    if (results.geo_contextual_data) {
      if (results.geo_contextual_type === 'geojson') {
        geoContextualLayer = {
          id: 'geo_contextual_polygon',
          type: 'geojson',
          config: {
            dataId: 'geo_contextual_data',
            label: 'Geo-Contextual Polygons',
            isVisible: true,
            columns: {
              geojson: '_geojson'
            },
            visConfig: {
              opacity: 0.85,
              filled: true,
              stroked: true
            }
          }
        };
      } else if (results.geo_contextual_type === 'csv') {
        geoContextualLayer = {
          id: 'geo_contextual_point',
          type: 'point',
          config: {
            dataId: 'geo_contextual_data',
            label: 'Geo-Contextual Points',
            isVisible: true,
            columns: {
              lat: 'latitude',
              lng: 'longitude'
            },
            visConfig: {
              radius: 10,
              opacity: 0.8,
              filled: true
            }
          }
        };
      }
    }

    const layers = [
      dynamicPathwayLayer
    ];

    if (analysisType === 'continuous' && results.hpd_polygons && results.hpd_polygons.features && results.hpd_polygons.features.length > 0) {
      layers.push({
        id: 'hpd_polygons_geojson',
        type: 'geojson',
        config: {
          dataId: 'hpd_polygons',
          label: 'HPD Polygons',
          isVisible: true,
          columns: {
            geojson: '_geojson'
          },
          visConfig: {
            opacity: 0.2,
            filled: true,
            stroked: false,
            colorRange: {
              name: 'Colorblind Friendly',
              type: 'sequential',
              category: 'Custom',
              colors: ['#D6DEBF', '#95C590', '#58A690', '#49828A', '#415F79', '#383C65']
            }
          },
          visualChannels: {
            colorField: {
              name: 'hpd_level',
              type: 'integer'
            },
            colorScale: 'quantile'
          }
        }
      });
    }

    if (analysisType === 'discrete' && results.aggregated_migration_network) {
      layers.push(aggregatedMigrationNetworkLayer);
    }

    if (geoContextualLayer) {
      layers.push(geoContextualLayer);
    }

    const keplerConfig = {
      version: 'v1',
      config: {
        mapState: {
          latitude: 35.0,
          longitude: 105.0,
          zoom: 3.8
        },
        mapStyle: mapStyleConfig,
        visState: {
          layers: layers
        }
      }
    };

    dispatch(addDataToMap({
      datasets: datasets,
      options: {
        centerMap: true,
        keepExistingConfig: true
      },
      config: keplerConfig
    }));

    setVisualized(true);
    setActiveTab('render');
    if (onResultsChange) {
      onResultsChange(results);
    }
  };

  const handleReset = () => {
    setEnvType('none');
    setEnvRegionsMap(null);
    setEnvRegionsData(null);
    setEnvRegionsLocCol('');
    setEnvRegionsLocVar('');
    setEnvRasterMap(null);
    setEnvRasterTiffFiles([]);
    setEnvRasterLocVar('');
    setEnvRasterLocList(null);
    setEnvRasterMode('static');

    setTreeFile(null);
    setLocationFile(null);
    setLogFile(null);
    setMostRecentTip('');
    setDateFormat('YYYY-MM-DD');
    setLocationTrait('');
    setBfThreshold(3.0);
    setBurnin(0.1);
    setIsAdvancedOpen(false);
    setReproject(false);
    setReprojectSource('');
    setReprojectTarget('');
    setReprojectLat('');
    setReprojectLon('');
    setTrim(false);
    setReferencedFile(null);
    setTrimPrimaryKey('');
    setTrimForeignKey('');
    setTrimNullQueries('');
    setError(null);
    setResults(null);
    setVisualized(false);
    setUserMapboxToken('');
    setEnableTianditu(false);
    setActiveTab('config');
  };

  return (
    <PanelContainer>
      <PanelHeader>
        <Title>
          {activeTab === 'config' ? 'SpreadGL Pipeline Setup' : 'Workspace'}
        </Title>
      </PanelHeader>

      <ScrollableContent>
        {activeTab === 'config' && (
          <form onSubmit={handleSubmit}>
            <ToggleGroup>
              <ToggleBtn 
                type="button" 
                $active={analysisType === 'discrete'} 
                onClick={() => setAnalysisType('discrete')}
              >
                Discrete
              </ToggleBtn>
              <ToggleBtn 
                type="button" 
                $active={analysisType === 'continuous'} 
                onClick={() => setAnalysisType('continuous')}
              >
                Continuous
              </ToggleBtn>
            </ToggleGroup>

            <FileInput 
              label="Tree File (.tree)" 
              accept=".trees,.tree" 
              file={treeFile} 
              onChange={setTreeFile} 
              required={true}
            />

            {analysisType === 'discrete' && (
              <FileInput 
                label="Location List (.csv)" 
                accept=".csv" 
                file={locationFile} 
                onChange={setLocationFile} 
                required={true}
              />
            )}

            <InputGroup>
              <Label>Location Trait *</Label>
              <TextInput 
                type="text" 
                placeholder="e.g. 'state'; 'location'; 'location1,location2'" 
                value={locationTrait} 
                onChange={e => setLocationTrait(e.target.value)}
                required
              />
            </InputGroup>

            <InputGroup>
              <Label>Most Recent Tip Date *</Label>
              <TextInput 
                type="text" 
                placeholder="e.g. 2023.12 or 2023-05-12" 
                value={mostRecentTip} 
                onChange={e => setMostRecentTip(e.target.value)} 
                required
              />
            </InputGroup>

            <InputGroup>
              <Label>Date Format</Label>
              <TextInput 
                type="text" 
                placeholder="YYYY-MM-DD or decimal" 
                value={dateFormat} 
                onChange={e => setDateFormat(e.target.value)}
              />
            </InputGroup>

            <div style={{ marginTop: '24px', borderTop: '1px solid rgba(16, 107, 163, 0.15)', paddingTop: '16px' }}>
              <Label style={{ color: '#106ba3', fontSize: '14px', marginBottom: '16px' }}>Bayes Factors</Label>
              
              <FileInput 
                label="BEAST Log (.log)" 
                accept=".log,.txt" 
                file={logFile} 
                onChange={setLogFile} 
                required={false}
              />
              
              {logFile && (
                <>
                  <SliderGroup style={{ marginTop: '16px' }}>
                    <SliderHeader>
                      <span>Burn-in Fraction</span>
                      <span style={{ color: '#106ba3' }}>{burnin.toFixed(2)}</span>
                    </SliderHeader>
                    <SliderInput 
                      type="range" 
                      min="0.0" 
                      max="0.9" 
                      step="0.01" 
                      value={burnin} 
                      onChange={e => setBurnin(parseFloat(e.target.value))}
                    />
                  </SliderGroup>

                  <SliderGroup style={{ marginTop: '16px' }}>
                    <SliderHeader>
                      <span>Aggregated Network BF Threshold</span>
                      <span style={{ color: '#106ba3' }}>{bfThreshold.toFixed(1)}</span>
                    </SliderHeader>
                    <SliderInput 
                      type="range" 
                      min="0" 
                      max="200" 
                      step="0.5" 
                      value={bfThreshold} 
                      onChange={e => setBfThreshold(parseFloat(e.target.value))}
                    />
                  </SliderGroup>
                </>
              )}

              <div style={{ marginTop: '12px', fontSize: '0.8rem', color: '#64748b', lineHeight: '1.4' }}>
                Upload your BEAST log to calculate and attach Bayes Factors to all spread routes. Routes in the Aggregated Network with a Bayes Factor below the threshold are filtered out during setup.
              </div>
            </div>

            {/* Geo-Contextual Data Section */}
            <div style={{ marginTop: '24px', borderTop: '1px solid rgba(16, 107, 163, 0.15)', paddingTop: '16px' }}>
              <Label style={{ color: '#106ba3', fontSize: '14px' }}>Geo-Contextual Data</Label>
              <EnvToggleGroup>
                <EnvToggleBtn 
                  type="button" 
                  $active={envType === 'none'} 
                  onClick={() => setEnvType('none')}
                >
                  None
                </EnvToggleBtn>
                <EnvToggleBtn 
                  type="button" 
                  $active={envType === 'regions'} 
                  onClick={() => setEnvType('regions')}
                >
                  Regional Polygons (GeoJSON)
                </EnvToggleBtn>
                <EnvToggleBtn 
                  type="button" 
                  $active={envType === 'raster'} 
                  onClick={() => setEnvType('raster')}
                >
                  Environmental Rasters (GeoTIFF)
                </EnvToggleBtn>
              </EnvToggleGroup>

              {envType === 'regions' && (
                <SubSection>
                  <FileInput 
                    label="Upload Boundary Map (.geojson)" 
                    accept=".geojson" 
                    file={envRegionsMap} 
                    onChange={setEnvRegionsMap} 
                    required={true}
                  />
                  <FileInput 
                    label="Tabular Data (.csv)" 
                    accept=".csv" 
                    file={envRegionsData} 
                    onChange={setEnvRegionsData} 
                    required={true}
                  />
                  <InputGroup>
                    <Label>Location Column *</Label>
                    <TextInput 
                      type="text" 
                      placeholder="e.g. province" 
                      value={envRegionsLocCol} 
                      onChange={e => setEnvRegionsLocCol(e.target.value)} 
                      required={envType === 'regions'}
                    />
                  </InputGroup>
                  <InputGroup>
                    <Label>Location Variable *</Label>
                    <TextInput 
                      type="text" 
                      placeholder="e.g. 'NAME_1'; 'state_name'; 'id'" 
                      value={envRegionsLocVar} 
                      onChange={e => setEnvRegionsLocVar(e.target.value)} 
                      required={envType === 'regions'}
                    />
                  </InputGroup>
                </SubSection>
              )}

              {envType === 'raster' && (
                <SubSection>
                  <FileInput 
                    label="Upload Boundary Map (.geojson)" 
                    accept=".geojson" 
                    file={envRasterMap} 
                    onChange={setEnvRasterMap} 
                    required={true}
                  />
                  <FileInput 
                    label="Raster TIFFs Directory" 
                    accept=".tif,.tiff" 
                    file={envRasterTiffFiles} 
                    onChange={setEnvRasterTiffFiles} 
                    required={true}
                    directory={true}
                  />
                  <FileInput 
                    label="Location List (.txt)" 
                    accept=".txt" 
                    file={envRasterLocList} 
                    onChange={setEnvRasterLocList} 
                    required={true}
                  />
                  <InputGroup>
                    <Label>Location Variable *</Label>
                    <TextInput 
                      type="text" 
                      placeholder="e.g. 'NAME_1'; 'state_name'; 'id'" 
                      value={envRasterLocVar} 
                      onChange={e => setEnvRasterLocVar(e.target.value)} 
                      required={envType === 'raster'}
                    />
                  </InputGroup>
                  <InputGroup>
                    <Label>Raster Mode</Label>
                    <ToggleGroup style={{ marginTop: '5px', marginBottom: '5px' }}>
                      <ToggleBtn 
                        type="button" 
                        $active={envRasterMode === 'static'} 
                        onClick={() => setEnvRasterMode('static')}
                      >
                        Static
                      </ToggleBtn>
                      <ToggleBtn 
                        type="button" 
                        $active={envRasterMode === 'dynamic'} 
                        onClick={() => setEnvRasterMode('dynamic')}
                      >
                        Dynamic
                      </ToggleBtn>
                    </ToggleGroup>
                  </InputGroup>
                </SubSection>
              )}
            </div>

            {/* Advanced Accordion: Reprojection & Trimming */}
            <Accordion>
              <AccordionHeader onClick={() => setIsAdvancedOpen(!isAdvancedOpen)}>
                <span>Advanced Parameters</span>
                <svg 
                  width="14" 
                  height="14" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="2.5"
                  style={{ 
                    transform: isAdvancedOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 0.2s ease'
                  }}
                >
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </AccordionHeader>

              <AccordionContent $isOpen={isAdvancedOpen}>
                <CheckboxContainer>
                  <CheckboxInput 
                    type="checkbox" 
                    checked={reproject} 
                    onChange={e => setReproject(e.target.checked)} 
                  />
                  Reproject Coordinates
                </CheckboxContainer>

                {reproject && (
                  <SubSection>
                    <InputGroup>
                      <Label>Source EPSG</Label>
                      <TextInput 
                        type="text" 
                        placeholder="e.g. 4326" 
                        value={reprojectSource} 
                        onChange={e => setReprojectSource(e.target.value)} 
                        required={reproject}
                      />
                    </InputGroup>
                    <InputGroup>
                      <Label>Target EPSG</Label>
                      <TextInput 
                        type="text" 
                        placeholder="e.g. 3857" 
                        value={reprojectTarget} 
                        onChange={e => setReprojectTarget(e.target.value)} 
                        required={reproject}
                      />
                    </InputGroup>
                    <InputGroup>
                      <Label>Latitude Field Keys</Label>
                      <TextInput 
                        type="text" 
                        placeholder="e.g. latitude, lat" 
                        value={reprojectLat} 
                        onChange={e => setReprojectLat(e.target.value)} 
                        required={reproject}
                      />
                    </InputGroup>
                    <InputGroup>
                      <Label>Longitude Field Keys</Label>
                      <TextInput 
                        type="text" 
                        placeholder="e.g. longitude, lon" 
                        value={reprojectLon} 
                        onChange={e => setReprojectLon(e.target.value)} 
                        required={reproject}
                      />
                    </InputGroup>
                  </SubSection>
                )}

                <CheckboxContainer>
                  <CheckboxInput 
                    type="checkbox" 
                    checked={trim} 
                    onChange={e => setTrim(e.target.checked)} 
                  />
                  Outlier Detection
                </CheckboxContainer>
                <div style={{ fontSize: '11.5px', color: '#64748b', marginTop: '-8px', marginBottom: '12px', paddingLeft: '22px', lineHeight: '1.4' }}>
                  Remove coordinate outliers beyond a specified standard deviation to clean noisy datasets.
                </div>

                {trim && (
                  <SubSection>
                    <FileInput 
                      label="Referenced CSV" 
                      accept=".csv" 
                      file={referencedFile} 
                      onChange={setReferencedFile} 
                      required={trim}
                    />
                    <InputGroup>
                      <Label>Primary Key</Label>
                      <TextInput 
                        type="text" 
                        placeholder="e.g. id" 
                        value={trimPrimaryKey} 
                        onChange={e => setTrimPrimaryKey(e.target.value)} 
                        required={trim}
                      />
                    </InputGroup>
                    <InputGroup>
                      <Label>Foreign Key</Label>
                      <TextInput 
                        type="text" 
                        placeholder="e.g. tree_id" 
                        value={trimForeignKey} 
                        onChange={e => setTrimForeignKey(e.target.value)} 
                        required={trim}
                      />
                    </InputGroup>
                    <InputGroup>
                      <Label>Null Query Fields</Label>
                      <TextInput 
                        type="text" 
                        placeholder="e.g. location, country" 
                        value={trimNullQueries} 
                        onChange={e => setTrimNullQueries(e.target.value)} 
                        required={trim}
                      />
                    </InputGroup>
                  </SubSection>
                )}
              </AccordionContent>
            </Accordion>

            <SubmitButton type="submit" style={{ marginTop: '24px' }}>
              Run Pipeline
            </SubmitButton>
          </form>
        )}

        {activeTab === 'staging' && (
          <div>
            {loading && (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <Spinner />
                <StatusText>Processing Phylogeographic Data...</StatusText>
              </div>
            )}

            {error && (
              <div>
                {error.includes("Location Mismatch") ? (
                  <LocationMismatchAlert>
                    <AlertHeader>
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                      </svg>
                      Location Mismatch Detected
                    </AlertHeader>
                    <div style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: '1.5' }}>
                      The backend found locations in the tree that are not present in your locations list.
                    </div>
                    <LocationList>
                      {error}
                    </LocationList>
                  </LocationMismatchAlert>
                ) : (
                  <ErrorCard>
                    <strong>Pipeline Failed:</strong><br />
                    {error}
                  </ErrorCard>
                )}
                <SubmitButton onClick={() => setActiveTab('config')}>
                  Back to Setup
                </SubmitButton>
              </div>
            )}

            {!loading && !error && (
              <div>
                {/* 1. Results / File List if results exist */}
                {results ? (
                  <div>
                    <StatusText style={{ color: '#106ba3', fontSize: '16px', fontWeight: 'bold', fontFamily: "'Outfit', sans-serif" }}>
                      Pipeline Processed Successfully!
                    </StatusText>
                    
                    <FileList>
                      {results.spatial_data && (
                        <FileCard>
                          <FileCardLeft>
                            <FileName>Spatial Data GeoJSON</FileName>
                            <FileDetails>
                              {results.spatial_data.features?.length || 0} features loaded
                            </FileDetails>
                          </FileCardLeft>
                          <DownloadBtn onClick={() => handleDownload('spatial_data.geojson', results.spatial_data, false)}>
                            Download
                          </DownloadBtn>
                        </FileCard>
                      )}

                      {results.dynamic_pathway && (
                        <FileCard>
                          <FileCardLeft>
                            <FileName>Dynamic Pathway GeoJSON</FileName>
                            <FileDetails>
                              {results.dynamic_pathway.features?.length || 0} features loaded
                            </FileDetails>
                          </FileCardLeft>
                          <DownloadBtn onClick={() => handleDownload('dynamic_pathway.geojson', results.dynamic_pathway, false)}>
                            Download
                          </DownloadBtn>
                        </FileCard>
                      )}

                      {results.hpd_polygons && results.hpd_polygons.features && results.hpd_polygons.features.length > 0 && (
                        <FileCard>
                          <FileCardLeft>
                            <FileName>HPD Polygons GeoJSON</FileName>
                            <FileDetails>
                              {results.hpd_polygons.features.length} features loaded
                            </FileDetails>
                          </FileCardLeft>
                          <DownloadBtn onClick={() => handleDownload('hpd_polygons.geojson', results.hpd_polygons, false)}>
                            Download
                          </DownloadBtn>
                        </FileCard>
                      )}

                      {analysisType === 'discrete' && results.aggregated_migration_network && (
                        <FileCard>
                          <FileCardLeft>
                            <FileName>Aggregated Migration Network GeoJSON</FileName>
                            <FileDetails>
                              {results.aggregated_migration_network.features?.length || 0} features loaded
                            </FileDetails>
                          </FileCardLeft>
                          <DownloadBtn onClick={() => handleDownload('aggregated_migration_network.geojson', results.aggregated_migration_network, false)}>
                            Download
                          </DownloadBtn>
                        </FileCard>
                      )}

                      {results.geo_contextual_data && (
                        <div style={{ marginTop: '16px', borderTop: '1px solid rgba(16, 107, 163, 0.15)', paddingTop: '16px' }}>
                          <Label style={{ fontSize: '14px', color: '#106ba3', marginBottom: '10px' }}>
                            Geo-Contextual Data Layers
                          </Label>
                          <FileCard>
                            <FileCardLeft>
                              <FileName>
                                {results.geo_contextual_type === 'geojson' ? 'Regional Polygons' : 'Environmental Rasters'}
                              </FileName>
                              <FileDetails>
                                Type: {results.geo_contextual_type?.toUpperCase()}
                              </FileDetails>
                            </FileCardLeft>
                            <DownloadBtn 
                              onClick={() => handleDownload(
                                results.geo_contextual_type === 'geojson' ? 'regional_polygons.geojson' : 'environmental_rasters.csv',
                                results.geo_contextual_data,
                                results.geo_contextual_type === 'csv'
                              )}
                            >
                              Download
                            </DownloadBtn>
                          </FileCard>
                        </div>
                      )}
                    </FileList>
                  </div>
                ) : (
                  <div style={{ marginBottom: '24px' }}>
                    <Label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px', color: '#106ba3', fontWeight: '700' }}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ color: '#106ba3' }}>
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="17 8 12 3 7 8"></polyline>
                        <line x1="12" y1="3" x2="12" y2="15"></line>
                      </svg>
                      Direct Render: Load Saved Results
                    </Label>
                    <div style={{ fontSize: '11.5px', color: '#64748b', marginBottom: '12px', lineHeight: '1.4' }}>
                      Bypass the backend pipeline by loading previously generated SpreadGL .geojson or .csv files directly to the map.
                    </div>
                    <input 
                      type="file" 
                      accept=".geojson,.json,.csv" 
                      ref={directInputRef} 
                      style={{ display: 'none' }} 
                      onChange={handleDirectUpload} 
                    />
                    <DirectUploadCard onClick={() => directInputRef.current?.click()}>
                      <span style={{ fontSize: '14px', fontWeight: '600', color: '#475569' }}>
                        Click to select a file (.geojson, .json, .csv)
                      </span>
                    </DirectUploadCard>
                  </div>
                )}

                {/* 2. Map styling settings (ALWAYS visible) */}
                <div style={{ marginTop: '24px', borderTop: '1px solid rgba(16, 107, 163, 0.15)', paddingTop: '20px', marginBottom: '20px' }}>
                  <form onSubmit={e => e.preventDefault()}>
                    <Label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: '#106ba3', fontWeight: '600' }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ color: '#106ba3' }}>
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                      </svg>
                      Mapbox Access Token (Optional)
                    </Label>
                    <div style={{ fontSize: '11px', color: '#64748b', marginBottom: '8px', lineHeight: '1.4' }}>
                      Enter your own Mapbox API Token to unlock Mapbox Premium styles (Satellite, Dark, Light, Muted Night, etc.).
                    </div>
                    <TextInput 
                      type="password" 
                      placeholder="pk.ey..." 
                      value={userMapboxToken} 
                      onChange={e => {
                        e.preventDefault();
                        setUserMapboxToken(e.target.value);
                      }}
                      onKeyDown={e => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                        }
                      }}
                    />
                    <div style={{ marginTop: '6px', fontSize: '11px' }}>
                      <a href="https://account.mapbox.com/auth/signup/" target="_blank" rel="noopener noreferrer" style={{ color: '#1e88e5', textDecoration: 'underline' }}>
                        Get your free Mapbox API key here
                      </a>
                    </div>
                  </form>
                </div>

                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', marginTop: '20px', padding: '12px 16px', background: 'rgba(16, 107, 163, 0.04)', borderRadius: '8px', border: '1px solid rgba(16, 107, 163, 0.12)', marginBottom: '16px' }}>
                  <input 
                    type="checkbox" 
                    id="enable-tianditu-checkbox" 
                    checked={enableTianditu} 
                    onChange={e => setEnableTianditu(e.target.checked)}
                    style={{ width: '18px', height: '18px', cursor: 'pointer', marginTop: '2px' }}
                  />
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <label htmlFor="enable-tianditu-checkbox" style={{ fontSize: '13px', color: '#106ba3', fontWeight: '600', cursor: 'pointer', userSelect: 'none' }}>
                      Enable Tianditu Basemaps (China Borders)
                    </label>
                    <span style={{ fontSize: '11px', color: '#64748b', marginTop: '4px', lineHeight: '1.4' }}>
                      Loads official Chinese standard maps (satellite/vector/terrain).
                    </span>
                  </div>
                </div>

                {/* 3. Action Buttons */}
                {results ? (
                  <SubmitButton onClick={handleVisualize}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                    Apply to Map
                  </SubmitButton>
                ) : (
                  <SubmitButton onClick={() => setActiveTab('render')}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                    Go to Map
                  </SubmitButton>
                )}

                <SecondaryButton onClick={handleReset} style={{ marginTop: '12px', border: '1px solid rgba(229, 62, 62, 0.4)', color: '#fca5a5' }}>
                  Reset / Clear All
                </SecondaryButton>
              </div>
            ) }
          </div>
        )}
      </ScrollableContent>
    </PanelContainer>
  );
}
