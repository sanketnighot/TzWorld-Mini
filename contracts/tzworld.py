import smartpy as sp  # type: ignore

FA2 = sp.io.import_script_from_url("file:contracts/utils/fa2.py")
Address = sp.io.import_script_from_url("file:contracts/utils/address.py")
tzcard_contract = sp.io.import_script_from_url("file:contracts/tzcard.py")
usdt_contract = sp.io.import_script_from_url("file:contracts/usdt.py")


if __name__ == "__main__":

    @sp.add_test("TzWorld-Mini")
    def test():
        sc = sp.test_scenario()
        sc.h1("TzWorld-Mini")
        sc.table_of_contents()

        token_md = FA2.make_metadata(name="USDt-token", decimals=6, symbol="USDt")

        usdt = usdt_contract.USDT(
            admin=Address.admin,
            metadata=sp.utils.metadata_of_url("http://example.com"),
            token_metadata=token_md,
        )

        sc.register(usdt)

        tzcard = tzcard_contract.TzCard(
            admin=Address.admin,
            metadata=sp.utils.metadata_of_url(
                "ipfs://QmW8jPMdBmFvsSEoLWPPhaozN6jGQFxxkwuMLtVFqEy6Fb"
            ),
            token_address=usdt.address,
        )

        sc.register(tzcard)

        sc += usdt.mint([sp.record(amount=sp.nat(10_000), to_=Address.alice)]).run(
            sender=Address.admin, show=False
        )
        sc += usdt.mint([sp.record(amount=sp.nat(10_000), to_=Address.bob)]).run(
            sender=Address.admin, show=False
        )
        sc += usdt.mint([sp.record(amount=sp.nat(10_000), to_=Address.elon)]).run(
            sender=Address.admin, show=False
        )
        sc += usdt.mint([sp.record(amount=sp.nat(10_000), to_=Address.mark)]).run(
            sender=Address.admin, show=False
        )

        sc.h1("Initial Storage of all contracts")

        sc.h2("USDT")
        sc.show(sp.record(contract_address=usdt.address, initial_storage=usdt.data))

        sc.h2("TzCard")
        sc.show(sp.record(contract_address=tzcard.address, initial_storage=tzcard.data))

        metadata = sp.pack(
            "ipfs://bafyreibwl5hhjgrat5l7cmjlv6ppwghm6ijygpz2xor2r6incfcxnl7y3e/metadata.json"
        )

        sc.h1("TzCard - Minting")
        sc += tzcard.mint(
            sp.record(metadata=sp.map({"": metadata}), to_=Address.alice)
        ).run(sender=Address.admin)

        sc.h1("TzCard - Minting")
        sc += tzcard.mint(
            sp.record(metadata=sp.map({"": metadata}), to_=Address.bob)
        ).run(sender=Address.admin)

        sc.h1("TzCard - Minting")
        sc += tzcard.mint(
            sp.record(metadata=sp.map({"": metadata}), to_=Address.elon)
        ).run(sender=Address.admin)

        sc.h1("TzCard - Minting")
        sc += tzcard.mint(
            sp.record(metadata=sp.map({"": metadata}), to_=Address.mark)
        ).run(sender=Address.admin)

        sc.h1("TzCard - Depositing USDT")
        sc += usdt.update_operators(
            [
                sp.variant(
                    "add_operator",
                    sp.record(operator=tzcard.address, owner=Address.alice, token_id=0),
                )
            ]
        ).run(sender=Address.alice, show=False)
        sc += tzcard.deposit_tokens(card_id=sp.nat(0), token_amount=sp.nat(1_000)).run(
            sender=Address.alice
        )

        sc += usdt.update_operators(
            [
                sp.variant(
                    "add_operator",
                    sp.record(operator=tzcard.address, owner=Address.bob, token_id=0),
                )
            ]
        ).run(sender=Address.bob, show=False)
        sc += tzcard.deposit_tokens(card_id=sp.nat(1), token_amount=sp.nat(8_000)).run(
            sender=Address.bob
        )

        sc += usdt.update_operators(
            [
                sp.variant(
                    "add_operator",
                    sp.record(operator=tzcard.address, owner=Address.elon, token_id=0),
                )
            ]
        ).run(sender=Address.elon, show=False)
        sc += tzcard.deposit_tokens(card_id=sp.nat(2), token_amount=sp.nat(3_000)).run(
            sender=Address.elon
        )

        sc += usdt.update_operators(
            [
                sp.variant(
                    "add_operator",
                    sp.record(operator=tzcard.address, owner=Address.mark, token_id=0),
                )
            ]
        ).run(sender=Address.mark, show=False)
        sc += tzcard.deposit_tokens(card_id=sp.nat(3), token_amount=sp.nat(6_000)).run(
            sender=Address.mark
        )

        sc.h1("TzCard - Withdrawing USDT")
        sc += tzcard.withdraw_tokens(card_id=sp.nat(1), token_amount=sp.nat(840)).run(
            sender=Address.bob
        )

        sc.h1("TzCard - Transfer Card")
        sc += tzcard.transfer_card(
            from_=Address.alice, to_=Address.bob, card_id=sp.nat(0)
        ).run(sender=Address.alice)

        for i in range(0, 4):
            sc.show(sp.record(card_id = i , card_owner = tzcard.get_card_owner(i), is_locked = tzcard.is_card_locked(i),locked_owner = tzcard.get_locked_tokens(i)))
