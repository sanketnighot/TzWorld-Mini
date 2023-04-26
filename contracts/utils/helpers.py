import smartpy as sp  # type: ignore

Errors = sp.io.import_script_from_url("file:contracts/utils/errors.py")


class Helpers(sp.Contract):
    def __init__(self):
        pass

    def is_stakeholder(self):
        """
        This function verifies if the sender is a stakeholder in the smart contract.
        """
        sp.verify(self.data.stakeholders.contains(sp.sender), Errors.NotStakeholder)

    def is_current_player(self, player_id):
        sp.verify_equal(player_id, self.data.current_player, Errors.NotYourTurn)

    def get_card_details(self, card_id):
        card_details = sp.local(
            "card_details",
            sp.view(
                "get_card_details",
                self.data.tzcard_contract,
                card_id,
                t=sp.TRecord(
                    card_id=sp.TNat,
                    card_owner=sp.TAddress,
                    card_details=sp.TRecord(
                        locked_tokens=sp.TNat, card_locked=sp.TBool
                    ),
                ),
            ).open_some(),
        )
        return card_details.value

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
            self.data.usdt_contract,
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

    def update_current_player(self):
        pass