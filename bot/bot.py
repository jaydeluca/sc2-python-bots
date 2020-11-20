import sc2
from sc2 import BotAI, Race, UnitTypeId, AbilityId
from sc2.ids.upgrade_id import UpgradeId
import random


class CompetitiveBot(BotAI):
    def __init__(self):
        # Initialize inherited class
        sc2.BotAI.__init__(self)
        self.proxy_built = False

    NAME: str = "CompetitiveBot"
    """This bot's name"""
    RACE: Race = Race.Protoss
    """This bot's Starcraft 2 race.
    Options are:
        Race.Terran
        Race.Zerg
        Race.Protoss
        Race.Random
    """

    async def on_start(self):
        print("Game started")
        # Do things here before the game starts

    async def on_step(self, iteration):

        if not self.townhalls.ready:
        # Attack with all workers if we don't have any nexuses left, attack-move on enemy spawn (doesn't work on 4 player map) so that probes auto attack on the way
            for worker in self.workers:
                worker.attack(self.enemy_start_locations[0])
            return
        else:
            nexus = self.townhalls.ready.random

        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.chrono()
        await self.build_gateway()
        await self.build_forge()
        await self.train_units()
        await self.build_gas()
        await self.build_cyber_core()
        await self.build_four_gates()
        await self.warpgate_research()
        await self.attack()

        # Build proxy pylon
        if (
            self.structures(UnitTypeId.CYBERNETICSCORE).amount >= 1
            and not self.proxy_built
            and self.can_afford(UnitTypeId.PYLON)
        ):
            p = self.game_info.map_center.towards(self.enemy_start_locations[0], 20)
            await self.build(UnitTypeId.PYLON, near=p)
            self.proxy_built = True        # Build proxy pylon
        if (
            self.structures(UnitTypeId.CYBERNETICSCORE).amount >= 1
            and not self.proxy_built
            and self.can_afford(UnitTypeId.PYLON)
        ):
            p = self.game_info.map_center.towards(self.enemy_start_locations[0], 20)
            await self.build(UnitTypeId.PYLON, near=p)
            self.proxy_built = True

        # Train probe on nexuses that are undersaturated (avoiding distribute workers functions)
        # if nexus.assigned_harvesters < nexus.ideal_harvesters and nexus.is_idle:
        if self.supply_workers + self.already_pending(UnitTypeId.PROBE) < self.townhalls.amount * 22 and nexus.is_idle:
            if self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)

        # If we have less than 3 nexuses and none pending yet, expand
        if self.townhalls.ready.amount + self.already_pending(UnitTypeId.NEXUS) < 3:
            if self.can_afford(UnitTypeId.NEXUS):
                await self.expand_now()

        pass

    async def build_workers(self):
        nexus = self.townhalls.ready.random
        if (
            self.can_afford(UnitTypeId.PROBE)
            and nexus.is_idle 
            and self.workers.amount < self.townhalls.amount * 22
        ):
            nexus.train(UnitTypeId.PROBE)

    async def build_pylons(self):
        nexus = self.townhalls.ready.random
        position = nexus.position.towards(self.enemy_start_locations[0], 10)
        if (
            self.supply_left < 3 
            and self.already_pending(UnitTypeId.PYLON) == 0
            and self.can_afford(UnitTypeId.PYLON)
        ):
            await self.build(UnitTypeId.PYLON, near = position)

    async def build_gateway(self):
        if (
            self.structures(UnitTypeId.PYLON).ready
            and self.can_afford(UnitTypeId.GATEWAY)
            and not self.structures(UnitTypeId.GATEWAY)
        ):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.GATEWAY, near = pylon)

    async def build_gas(self):
        if self.structures(UnitTypeId.GATEWAY):
            for nexus in self.townhalls.ready:
                vgs = self.vespene_geyser.closer_than(15, nexus)
                for vg in vgs:
                    if not self.can_afford(UnitTypeId.ASSIMILATOR):
                        break
                    worker = self.select_build_worker(vg.position)
                    if worker is None:
                        break
                    if not self.gas_buildings or not self.gas_buildings.closer_than(1, vg):
                        worker.build(UnitTypeId.ASSIMILATOR, vg)
                        worker.stop(queue=True)

    async def build_cyber_core(self):
        if self.structures(UnitTypeId.PYLON).ready:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            if self.structures(UnitTypeId.GATEWAY).ready:
                if not self.structures(UnitTypeId.CYBERNETICSCORE):
                    if (
                        self.can_afford(UnitTypeId.CYBERNETICSCORE)
                        and self.already_pending(UnitTypeId.CYBERNETICSCORE) == 0
                    ):
                        await self.build(UnitTypeId.CYBERNETICSCORE, near = pylon)


    async def train_units(self):

        if self.structures(UnitTypeId.PYLON).ready:
            proxy = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])

        if self.structures(UnitTypeId.WARPGATE).amount == 0:
            for gateway in self.structures(UnitTypeId.GATEWAY).ready:
                if (
                    self.can_afford(UnitTypeId.ZEALOT)
                    and gateway.is_idle
                ):
                    gateway.train(UnitTypeId.ZEALOT)


        for warpgate in self.structures(UnitTypeId.WARPGATE).ready:
            abilities = await self.get_available_abilities(warpgate)
            if AbilityId.WARPGATETRAIN_STALKER in abilities:
                pos = proxy.position.to2.random_on_distance(4)
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
                if placement is None:
                    print("can't place")
                    return
                if self.units(UnitTypeId.STALKER).amount < 20:
                    warpgate.warp_in(UnitTypeId.STALKER, placement)

    async def build_four_gates(self):
        if (
            self.structures(UnitTypeId.PYLON).ready
            and self.can_afford(UnitTypeId.GATEWAY)
            and self.structures(UnitTypeId.GATEWAY).amount + self.structures(UnitTypeId.WARPGATE).amount  < 4
        ):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.GATEWAY, near = pylon)


    async def chrono(self):
        if self.structures(UnitTypeId.PYLON):
            nexus = self.townhalls.ready.random
            if (
                not self.structures(UnitTypeId.CYBERNETICSCORE).ready
                and self.structures(UnitTypeId.PYLON).amount > 0
            ):
                if nexus.energy >= 50:
                    nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
            else:
                if nexus.energy >= 50:
                    cybercore = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
                    nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, cybercore)


    async def warpgate_research(self):
        if (
            self.structures(UnitTypeId.CYBERNETICSCORE).ready
            and self.can_afford(AbilityId.RESEARCH_WARPGATE)
            and self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 0
        ):
            cybercore = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            cybercore.research(UpgradeId.WARPGATERESEARCH)


    async def attack(self):
        stalkers = self.units(UnitTypeId.STALKER).ready.idle
        stalker_count = self.units(UnitTypeId.STALKER).amount

        zealots = self.units(UnitTypeId.ZEALOT).ready.idle
        zealot_count = self.units(UnitTypeId.ZEALOT).amount
        total_unit_count = zealot_count + stalker_count

        attack_threshold = 15
        
        for stalker in stalkers:
            if total_unit_count > attack_threshold:
                stalker.attack(self.enemy_start_locations[0])

        for zealot in zealots:
            if total_unit_count > attack_threshold:
                zealot.attack(self.enemy_start_locations[0])


    async def build_forge(self):
        if self.structures(UnitTypeId.PYLON).ready:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            if self.structures(UnitTypeId.CYBERNETICSCORE).ready:
                if not self.structures(UnitTypeId.FORGE):
                    if (
                        self.can_afford(UnitTypeId.FORGE)
                        and self.already_pending(UnitTypeId.FORGE) == 0
                    ):
                        await self.build(UnitTypeId.FORGE, near = pylon)

    def on_end(self, result):
        print("Game ended.")
        # Do things here after the game ends
