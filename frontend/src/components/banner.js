// SPDX-License-Identifier: MIT
// Copyright contributors to the kepler.gl project

import React from 'react';
import styled from 'styled-components';
import { Icons } from '@kepler.gl/components';

const StyledBanner = styled.div`
  align-items: center;
  background-color: ${props => props.$bgcolor};
  color: ${props => props.$fontcolor};
  display: flex;
  height: ${props => props.height}px;
  justify-content: space-between;
  padding: 0 40px;
  position: absolute;
  transition: top 1s;
  width: 100%;
  z-index: 9999;

  svg:hover {
    cursor: pointer;
  }

  top: ${props => (props.$visible ? 0 : -100)}px;
`;

const Banner = ({
  bgcolor = '#1F7CF4',
  fontcolor = '#FFFFFF',
  height = 30,
  children,
  onClose,
  show
}) => (
  <StyledBanner
    className="top-banner"
    $bgcolor={bgcolor}
    $fontcolor={fontcolor}
    height={height}
    $visible={show}
  >
    <div>{children}</div>
    <Icons.Delete height="14px" onClick={onClose} />
  </StyledBanner>
);

export default Banner;
