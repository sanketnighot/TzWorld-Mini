import smartpy as sp  # type: ignore

FA2 = sp.io.import_script_from_url("file:contracts/utils/fa2.py")
Address = sp.io.import_script_from_url("file:contracts/utils/address.py")
Errors = sp.io.import_script_from_url("file:contracts/utils/errors.py")


class TzCard(FA2.Admin, FA2.MintNft, FA2.Fa2Nft, FA2.OnchainviewBalanceOf):
    def __init__(self, admin, token_address, **kwargs):
        FA2.Fa2Nft.__init__(self, **kwargs)
        FA2.Admin.__init__(self, admin)
        self.update_initial_storage(
            cards_ledger=sp.big_map(
                l={},
                tkey=sp.TNat,
                tvalue=sp.TRecord(locked_tokens=sp.TNat, card_locked=sp.TBool),
            ),
            token_address=token_address,
            transaction_fees=sp.nat(2),
        )

    def transfer_tokens(self, from_, to_, amount_):
        transfer_params = sp.contract(
            sp.TList(
                sp.TRecord(
                    from_=sp.TAddress,
                    txs=sp.TList(
                        sp.TRecord(
                            amount=sp.TNat, to_=sp.TAddress, token_id=sp.TNat
                        ).layout(("to_", ("token_id", "amount")))
                    ),
                ).layout(("from_", "txs"))
            ),
            self.data.token_address,
            entry_point="transfer",
        ).open_some()

        transfer_data_params = sp.TList(
            sp.TRecord(
                from_=sp.TAddress,
                txs=sp.TList(
                    sp.TRecord(
                        amount=sp.TNat, to_=sp.TAddress, token_id=sp.TNat
                    ).layout(("to_", ("token_id", "amount")))
                ),
            ).layout(("from_", "txs"))
        )

        transfer_data = [
            sp.record(
                from_=from_,
                txs=[sp.record(amount=amount_, to_=to_, token_id=sp.nat(0))],
            )
        ]

        sp.transfer(
            sp.set_type_expr(transfer_data, transfer_data_params),
            sp.mutez(0),
            transfer_params,
        )

    @sp.entry_point
    def mint(self, params):
        sp.set_type(
            params,
            sp.TRecord(metadata=sp.TMap(sp.TString, sp.TBytes), to_=sp.TAddress).layout(
                ("to_", "metadata")
            ),
        )
        sp.verify(sp.sender == self.data.administrator, "FA2_NOT_ADMIN")
        compute_fa2_601 = sp.local("compute_fa2_601", self.data.next_token_id)
        self.data.token_metadata[compute_fa2_601.value] = sp.record(
            token_id=compute_fa2_601.value, token_info=params.metadata
        )
        self.data.ledger[compute_fa2_601.value] = params.to_
        self.data.next_token_id += 1
        self.data.cards_ledger[compute_fa2_601.value] = sp.record(
            locked_tokens=sp.nat(0), card_locked=sp.bool(False)
        )

    @sp.entry_point
    def deposit_tokens(self, card_id, token_amount):
        sp.set_type(card_id, sp.TNat)
        sp.set_type(token_amount, sp.TNat)
        sp.verify(self.data.ledger.contains(card_id), Errors.InvalidPlayerCard)
        fees = token_amount * self.data.transaction_fees // 100
        new_token_amount = sp.local("new_token_amount", sp.as_nat(token_amount - fees))
        self.data.cards_ledger[card_id].locked_tokens += new_token_amount.value
        self.transfer_tokens(from_=sp.sender, to_=sp.self_address, amount_=token_amount)
        self.transfer_tokens(
            from_=sp.self_address, to_=self.data.administrator, amount_=fees
        )

    @sp.entry_point
    def withdraw_tokens(self, card_id, token_amount):
        sp.set_type(card_id, sp.TNat)
        sp.set_type(token_amount, sp.TNat)
        sp.verify(self.data.ledger.contains(card_id), Errors.InvalidPlayerCard)
        sp.verify(self.data.ledger[card_id] == sp.sender, Errors.InvalidOwner)
        sp.verify(
            token_amount <= self.data.cards_ledger[card_id].locked_tokens,
            Errors.InsufficientAmount,
        )
        self.transfer_tokens(from_=sp.self_address, to_=sp.sender, amount_=token_amount)
        self.data.cards_ledger[card_id].locked_tokens = sp.as_nat(
            self.data.cards_ledger[card_id].locked_tokens - token_amount
        )

    @sp.entry_point
    def transfer_card(self, from_, to_, card_id):
        sp.verify(self.data.token_metadata.contains(card_id), "FA2_TOKEN_UNDEFINED")
        sp.verify(
            (sp.sender == from_)
            | (
                self.data.operators.contains(
                    sp.record(owner=from_, operator=sp.sender, token_id=card_id)
                )
            ),
            "FA2_NOT_OPERATOR",
        )
        sp.verify(~self.data.cards_ledger[card_id].card_locked, Errors.CardLocked)
        sp.verify(self.data.ledger[card_id] == from_, "FA2_INSUFFICIENT_BALANCE")
        self.data.ledger[card_id] = to_

    @sp.onchain_view()
    def get_card_owner(self, card_id):
        sp.set_type(card_id, sp.TNat)
        sp.result(self.data.ledger[card_id])

    @sp.onchain_view()
    def get_locked_tokens(self, card_id):
        sp.set_type(card_id, sp.TNat)
        sp.result(self.data.cards_ledger[card_id].locked_tokens)
    
    @sp.onchain_view()
    def is_card_locked(self, card_id):
        sp.set_type(card_id, sp.TNat)
        sp.result(self.data.cards_ledger[card_id].card_locked)


sp.add_compilation_target(
    "Compiled_TzCard_Contract",
    TzCard(
        admin=Address.admin,
        metadata=sp.utils.metadata_of_url(
            "ipfs://QmW8jPMdBmFvsSEoLWPPhaozN6jGQFxxkwuMLtVFqEy6Fb"
        ),
        token_address=sp.address("KT1USDT"),
    ),
    storage=None,
)
