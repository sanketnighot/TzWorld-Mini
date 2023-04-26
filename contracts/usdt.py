import smartpy as sp  # type: ignore

FA2 = sp.io.import_script_from_url("file:contracts/utils/fa2.py")
Address = sp.io.import_script_from_url("file:contracts/utils/address.py")
Errors = sp.io.import_script_from_url("file:contracts/utils/errors.py")


class USDT(
    FA2.Fa2SingleAsset,
    FA2.Admin,
    FA2.OnchainviewBalanceOf,
    FA2.MintSingleAsset,
    FA2.BurnSingleAsset,
):
    def __init__(self, admin, metadata, **kwargs):
        FA2.Fa2SingleAsset.__init__(self, metadata, **kwargs)
        FA2.Admin.__init__(self, admin)


sp.add_compilation_target(
    "Compiled_USDT_Contract",
    USDT(admin=Address.admin, metadata=sp.utils.metadata_of_url("http://example.com")),
)
