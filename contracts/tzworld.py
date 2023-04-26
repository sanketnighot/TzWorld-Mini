import smartpy as sp  # type: ignore

FA2 = sp.io.import_script_from_url("file:contracts/utils/fa2.py")
Address = sp.io.import_script_from_url("file:contracts/utils/address.py")
tzcard_contract = sp.io.import_script_from_url("file:contracts/tzcard.py")
game_engine_contract = sp.io.import_script_from_url("file:contracts/game_engine.py")
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
            token_operators=sp.set([Address.admin]),
        )
        sc.register(tzcard)
        
        game_engine = game_engine_contract.GameEngine(
            _stakeholders=sp.set([Address.admin]),
            _game_status=sp.variant("not_started", sp.unit),
            _game_fees=sp.nat(1),
            _tzcard_contract=tzcard.address,
            _usdt_contract=usdt.address,
        )
        sc.register(game_engine)
        
        sc += tzcard.add_operator(game_engine.address).run(sender=Address.admin, show=False)
        
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

        sc.h2("Game Engine")
        sc.show(sp.record(contract_address=game_engine.address, initial_storage=game_engine.data))

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
        
        sc.h1("TzCard - Enter Game")
        sc += usdt.update_operators(
            [
                sp.variant(
                    "add_operator",
                    sp.record(operator=game_engine.address, owner=Address.alice, token_id=0),
                )
            ]
        ).run(sender=Address.alice, show=False)
        sc += usdt.update_operators(
            [
                sp.variant(
                    "add_operator",
                    sp.record(operator=game_engine.address, owner=Address.bob, token_id=0),
                )
            ]
        ).run(sender=Address.bob, show=False)
        sc += usdt.update_operators(
            [
                sp.variant(
                    "add_operator",
                    sp.record(operator=game_engine.address, owner=Address.elon, token_id=0),
                )
            ]
        ).run(sender=Address.elon, show=False)
        sc += usdt.update_operators(
            [
                sp.variant(
                    "add_operator",
                    sp.record(operator=game_engine.address, owner=Address.mark, token_id=0),
                )
            ]
        ).run(sender=Address.mark, show=False)
        sc += game_engine.enter_game(sp.nat(2)).run(sender=Address.elon)
        sc += game_engine.enter_game(sp.nat(0)).run(sender=Address.alice)
        sc += game_engine.enter_game(sp.nat(3)).run(sender=Address.mark)
        sc += game_engine.enter_game(sp.nat(1)).run(sender=Address.bob)
        sc.show(game_engine.data)
        sc += game_engine.leave_game(sp.nat(3)).run(sender=Address.mark)
        sc.show(game_engine.data)
        sc += game_engine.enter_game(sp.nat(1)).run(sender=Address.bob, valid=False)
        sc.show(game_engine.data)
        sc += game_engine.leave_game(sp.nat(0)).run(sender=Address.alice)
        sc.show(game_engine.data)
        sc += game_engine.leave_game(sp.nat(1)).run(sender=Address.bob)
        sc.show(game_engine.data)
        sc += game_engine.enter_game(sp.nat(0)).run(sender=Address.alice)
        sc += game_engine.enter_game(sp.nat(3)).run(sender=Address.mark)
        sc += game_engine.enter_game(sp.nat(1)).run(sender=Address.bob)
