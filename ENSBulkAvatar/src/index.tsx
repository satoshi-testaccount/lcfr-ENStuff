// check VERSIONS in package.json and make sure you have latest versions of bs...
// fixed problem with unsupported chain 

import React from "react";
import ReactDOM from "react-dom";
import App from "./App";
import { DAppProvider } from "@usedapp/core";

import { Config, Mainnet, Goerli } from '@usedapp/core'
import { getDefaultProvider } from 'ethers'



const config: Config = {
  //readOnlyChainId: Mainnet.chainId,
  readOnlyChainId: Goerli.chainId,
  readOnlyUrls: {
    //[Mainnet.chainId]: getDefaultProvider('mainnet'),  // or goerli
    [Goerli.chainId]: getDefaultProvider('goerli'),  // or goerli

  },
}

ReactDOM.render(
  <React.StrictMode>
    <DAppProvider config={config}>
      <App />
    </DAppProvider>
  </React.StrictMode>,
  document.getElementById("root")
);
