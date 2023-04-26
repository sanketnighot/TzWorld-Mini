import smartpy as sp  # type: ignore

Address = sp.io.import_script_from_url("file:contracts/utils/address.py")
Errors = sp.io.import_script_from_url("file:contracts/utils/errors.py")
Helpers = sp.io.import_script_from_url("file:contracts/utils/helpers.py")

game_status_type = sp.TVariant(
    not_started=sp.TUnit,
    on_going=sp.TUnit,
    ended=sp.TUnit,
).layout(("not_started", ("on_going", "ended")))

player_status_type = sp.TVariant(
    active=sp.TUnit, inactive=sp.TNat, bankrupt=sp.TUnit
).layout(("active", ("inactive", "bankrupt")))

game_action_type = sp.TVariant(dice_roll=sp.TUnit, await_player_action=sp.TUnit).layout(
    ("dice_roll", "await_player_action")
)


class GameEngine(Helpers.Helpers):
    def __init__(
        self, _stakeholders, _game_status, _game_fees, _tzcard_contract, _usdt_contract
    ):
        self.init(
            stakeholders=_stakeholders,
            total_players=sp.nat(0),
            players_ledger=sp.map(
                tkey=sp.TNat,
                tvalue=sp.TRecord(
                    current_position=sp.TNat,
                    player_status=player_status_type,
                    doubles_on_dice=sp.TNat,
                    current_game_action=game_action_type,
                ),
            ),
            current_player=sp.nat(0),
            game_status=_game_status,
            game_fees=_game_fees,
            minimum_players=sp.nat(2),
            maximum_players=sp.nat(4),
            time_per_turn=sp.int(60),
            tzcard_contract=_tzcard_contract,
            usdt_contract=_usdt_contract,
        )
        self.init_type(
            sp.TRecord(
                stakeholders=sp.TSet(sp.TAddress),
                total_players=sp.TNat,
                players_ledger=sp.TMap(
                    sp.TNat,
                    sp.TRecord(
                        current_position=sp.TNat,
                        player_status=player_status_type,
                        doubles_on_dice=sp.TNat,
                        current_game_action=game_action_type,
                    ),
                ),
                current_player=sp.TNat,
                game_status=game_status_type,
                game_fees=sp.TNat,
                minimum_players=sp.TNat,
                maximum_players=sp.TNat,
                time_per_turn=sp.TInt,
                tzcard_contract=sp.TAddress,
                usdt_contract=sp.TAddress,
            )
        )
        Helpers.Helpers.__init__(self)

    @sp.entry_point
    def add_stakeholders(self, new_stakeholder):
        sp.set_type(new_stakeholder, sp.TAddress)
        self.is_stakeholder()
        self.data.stakeholders.add(new_stakeholder)

    @sp.entry_point
    def remove_stakeholders(self, remove_stakeholder):
        sp.set_type(remove_stakeholder, sp.TAddress)
        self.is_stakeholder()
        self.data.stakeholders.remove(remove_stakeholder)

    @sp.entry_point
    def enter_game(self, card_id):
        sp.set_type(card_id, sp.TNat)
        card_details = self.get_card_details(card_id)
        sp.verify(sp.sender == card_details.card_owner, Errors.InvalidOwner)
        sp.verify(~card_details.card_details.card_locked, Errors.CardLocked)
        self.transfer_tokens(
            from_=sp.sender, to_=sp.self_address, amount_=self.data.game_fees
        )
        sp.transfer(
            card_id,
            sp.mutez(0),
            sp.contract(
                sp.TNat, self.data.tzcard_contract, entry_point="lock_card"
            ).open_some(),
        )
        self.data.players_ledger[card_id] = sp.record(
            current_position=sp.nat(0),
            player_status=sp.variant("active", sp.unit),
            doubles_on_dice=sp.nat(0),
            current_game_action=sp.variant("dice_roll", sp.unit),
        )
        self.data.total_players += 1

    @sp.entry_point
    def leave_game(self, card_id):
        sp.set_type(card_id, sp.TNat)
        card_details = self.get_card_details(card_id)
        sp.verify(sp.sender == card_details.card_owner, Errors.InvalidOwner)
        sp.verify(self.data.players_ledger.contains(card_id), Errors.InvalidCardId)
        sp.transfer(
            card_id,
            sp.mutez(0),
            sp.contract(
                sp.TNat, self.data.tzcard_contract, entry_point="unlock_card"
            ).open_some(),
        )
        player_ledger_keys = sp.local(
            "player_ledger_keys", self.data.players_ledger.keys()
        )
        with sp.for_("player_key", player_ledger_keys.value) as player_key:
            with sp.if_(player_key == card_id):
                del self.data.players_ledger[player_key]
        self.data.total_players = abs(self.data.total_players - 1)


sp.add_compilation_target(
    "Compiled_GameEngine_Contract",
    GameEngine(
        _stakeholders=sp.set([Address.admin]),
        _game_status=sp.variant("not_started", sp.unit),
        _game_fees=sp.nat(1),
        _tzcard_contract=sp.address("KT1TzCard"),
        _usdt_contract=sp.address("KT1USDT"),
    ),
    storage=None,
)
