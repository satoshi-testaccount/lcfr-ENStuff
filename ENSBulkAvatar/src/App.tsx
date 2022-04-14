import { ChakraProvider, useDisclosure } from "@chakra-ui/react";
import theme from "./theme";
import Layout from "./components/Layout";
import ConnectButton from "./components/ConnectButton"; // import part of gui/functions 
import AccountModal from "./components/AccountModal"; // import part of gui/functions 
import Multicall from "./components/Multicall"; // import part of gui/functions 
import "@fontsource/inter";

function App() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  return (
    <ChakraProvider theme={theme}>
      <Layout>
        <ConnectButton handleOpenModal={onOpen} />
        <AccountModal isOpen={isOpen} onClose={onClose} />
        <Multicall />
      </Layout>
    </ChakraProvider>
  );
}

export default App;
