from eth_utils import function_signature_to_4byte_selector

from ethereum_dasm.evmdasm import EvmCode, Contract


class EvmContractService:

    def get_function_sighashes(self, bytecode):
        bytecode = clean_bytecode(bytecode)
        if bytecode is not None:
            evm_code = EvmCode(contract=Contract(bytecode=bytecode), static_analysis=False, dynamic_analysis=False)
            evm_code.disassemble(bytecode)
            basic_blocks = evm_code.basicblocks
            functions = set()
            if basic_blocks:
                for block in basic_blocks:
                    instructions = block.instructions
                    push4_instructions = [inst for inst in instructions if inst.name == 'PUSH4']
                    functions.update(set('0x' + inst.operand for inst in push4_instructions))
                return sorted(list(functions))
            else:
                return []
        else:
            return []


    def is_erc20_contract(self, function_sighashes):
        c = ContractWrapper(function_sighashes)
        return c.implements('totalSupply()') and \
               c.implements('balanceOf(address)') and \
               c.implements('transfer(address,uint256)') and \
               c.implements('transferFrom(address,address,uint256)') and \
               c.implements('approve(address,uint256)') and \
               c.implements('allowance(address,address)')

    def is_erc165_contract(self, function_sighashes):
        c = ContractWrapper(function_sighashes)
        return c.implements('supportsInterface(bytes4)')

    def is_erc721_contract(self, function_sighashes):
        c = ContractWrapper(function_sighashes)
        return c.implements('balanceOf(address)') and \
               c.implements('ownerOf(uint256)') and \
               c.implements_any_of('transfer(address,uint256)', 'transferFrom(address,address,uint256)') and \
               c.implements('approve(address,uint256)')

    def is_erc1155_contract(self, function_sighashes):
        c = ContractWrapper(function_sighashes)
        return c.implements_any_of('balanceOf(address,uint256)', 'balanceOfBatch(address[],uint256[])') and \
               c.implements('setApprovalForAll(address,bool)') and \
               c.implements('isApprovedForAll(address,address)') and \
               c.implements('safeTransferFrom(address,address,uint256,uint256,bytes)') and \
               c.implements('safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)')

def clean_bytecode(bytecode):
    if bytecode is None or bytecode == '0x':
        return None
    elif bytecode.startswith('0x'):
        return bytecode[2:]
    else:
        return bytecode


def get_function_sighash(signature):
    return '0x' + function_signature_to_4byte_selector(signature).hex()


class ContractWrapper:
    def __init__(self, sighashes):
        self.sighashes = sighashes

    def implements(self, function_signature):
        sighash = get_function_sighash(function_signature)
        return sighash in self.sighashes

    def implements_any_of(self, *function_signatures):
        return any(self.implements(function_signature) for function_signature in function_signatures)
