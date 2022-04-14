// hooks/index.ts
import { ethers } from "ethers";
import { Contract } from "@ethersproject/contracts";
import { useContractFunction, useCall } from "@usedapp/core";

import publicResolverAbi from "../abi/publicResolver.json";
import baseRegistrarAbi from "../abi/baseRegistrar.json";

import { baseRegistrar, publicResolver } from "../contracts"

const baseRegistrarInterface = new ethers.utils.Interface(baseRegistrarAbi);
//const ENS_REGISTRAR = new Contract(baseRegistrar, baseRegistrarInterface);   

const publicResolverInterface = new ethers.utils.Interface(publicResolverAbi);
const ENS_RESOLVER = new Contract(publicResolver, publicResolverInterface);

export function GetBalanceOf( address: any ) {
    const { value, error } =
      useCall(
        address &&
          baseRegistrar && {
            contract: new Contract(baseRegistrar, baseRegistrarInterface), // instance of called contract
            method: "balanceOf", // Method to be called
            args: [address], // Method arguments - address to be checked for balance
          }
      ) ?? {};
    if(error) {
      console.error(error.message)
      return undefined
    }
    return value?.[0]
  }

export function UseMultiCall() {
    const { state, send } = useContractFunction(ENS_RESOLVER, "multicall", {});
    return { state, send };
  }