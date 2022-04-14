// i dont even understand variables in JS :( 
// ignore mix usage of let, var, const thx

import React, { useState } from 'react';

import { ethers } from "ethers";

import {
  Flex,
  Text,
  Button,
} from "@chakra-ui/react";

import { GetBalanceOf, UseMultiCall } from "../hooks";

import { useEthers } from "@usedapp/core";
import publicResolverAbi from "../abi/publicResolver.json";

import Textarea from 'react-expanding-textarea'

export default function MultiAvatarSet() {

    const [input, setInput] = useState("");

    // get account and call balanceOf on ENS registrart contract
    const { account } = useEthers();
    const balance = GetBalanceOf(account);

    // init send() func params to the multicall() function in ENS contract
    const { send } = UseMultiCall();

    function sort(data:string){
        //console.log(data);
        var result = data.split("\n");

        var names = [];
        var urls = [];
    
        //console.log(result);
        for(var i = 0; i < result.length; i++) {
            //console.log(result[i]);

            var name_str = result[i].split(" ");
            //console.log(data2);

            names.push(name_str[0]);
            urls.push(name_str[1]);

            //console.log(names);
            //console.log(urls);
        }
        return [names, urls];
    }

    function get_settext_calldata(name:string, value:string) {
        const publicResolverInterface = new ethers.utils.Interface(publicResolverAbi);

        //console.log("name: "+name+" length: "+name.length);
        //console.log("value: "+value);
        const node = ethers.utils.namehash(name+".eth")
        const calldata = publicResolverInterface.encodeFunctionData("setText", [node, "avatar", value]);
        return calldata;
    }
    
    function DoMultiCall() {

        const [names_list, urls_list] = sort(input);
        const calldata: any = [];

        if(input === ""){
            alert("null data, try again.");
            return
        }
        if (names_list.length === urls_list.length){

            names_list.forEach(function (value, i) {
                const cd = get_settext_calldata(value, urls_list[i]);
                //console.log(cd);
                calldata.push(cd);
            });

            //console.log(calldata);

            send(calldata)

        } else {
            alert("names_list.length != urls_list.length check same amount of names as urls and try again.");
            return;
        }
    }
    
    return (
        <>
        <Flex direction="column" align="center" mt="2">
        <Text color="white" fontSize="lg">
            ENS NAME COUNT: {balance ? balance.toNumber() : 0 }
        </Text>
        <Textarea
            className="textarea"
            id="my-textarea"
            onChange={e => setInput(e.target.value)}
            rows="10"
            style={{ display: 'block', width: '550px' }}
        />
        <Button colorScheme="purple" onClick={DoMultiCall} mt="2">
        SET ENS AVATARS
        </Button>
        <Text color="white" fontSize="lg">
            USAGE:<br></br>
            Input one per line with no .ETH extension like shown below<br></br><br></br>
            coolethname1 http://url.to/avatar1.jpg<br></br>
            coolethname2 http://url.to/avatar2.jpg<br></br>
            coolethname3 http://url.to/avatar3.jpg<br></br><br></br>

            tips:<br></br> 
            lcfr.eth : 0x328eBc7bb2ca4Bf4216863042a960E3C64Ed4c10
        </Text>
        </Flex>
        </>
      )
    }

/*    
return (
    <Flex direction="column" align="center" mt="4">
      <Text color="white" fontSize="lg">
        ENS NAME COUNT: {balance ? balance.toNumber() : 0 }
      </Text>
      <Box mt={4}>
      <Input
              placeholder="ENS NAMES"
              textColor="white"
              mb={2}
              min={1}
              onChange={e => setInput(e.target.value)}
              size='lg'
        />
        <Button isFullWidth colorScheme="purple" onClick={DoMultiCall}>
        SET ENS AVATARS
        </Button>
      </Box>
    </Flex>
  );
}
*/