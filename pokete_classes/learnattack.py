"""Contains the LearnAttack class"""

import time
import random
import scrap_engine as se
import pokete_data as p_data
from pokete_general_use_fns import std_loop, liner, easy_exit_loop
from .input import ask_bool, ask_ok
from .ui_elements import ChooseBox, Box
from .detail import Detail
from .attack import Attack
from .event import _ev


class AttackInfo(Box):
    """Gives information about a certain attack
    ARGS:
        attack: The attack's name
        _map: se.Map this should be shown on"""

    def __init__(self, attack, _map):
        atc = Attack(attack)
        desc_label = se.Text(liner(atc.desc, 40))
        super().__init__(5 + len(desc_label.text.split("\n")),
                         sorted(len(i) for i in
                            desc_label.text.split("\n")
                            + [atc.label_type.text,
                               atc.label_factor.text])[-1] + 4, atc.name,
                         "q:close")
        self.map = _map
        self.add_ob(atc.label_type, 2, 1)
        self.add_ob(atc.label_factor, 2, 2)
        self.add_ob(se.Text(f"AP:{atc.max_ap}"), 2, 3)
        self.add_ob(desc_label, 2, 4)

    def __enter__(self):
        """Enter dunder for context management"""
        self.center_add(self.map)
        self.map.show()
        return self


class LearnAttack:
    """Lets a Pokete learn a new attack
    ARGS:
        poke: The Poke that should learn an attack
        _map: The se.Map this should happen on"""

    def __init__(self, poke, _map):
        self.map = _map
        self.poke = poke
        self.box = ChooseBox(6, 25, name="Attacks", info="1:Details, 2:Info")

    def __call__(self, attack=None):
        """Starts the learning process
        ARGS:
            attack: The attack's name that should be learned, if None a fitting
                    attack will be chosen randomly
        RETURNS:
            bool: Whether or not the attack was learned"""

        attacks = p_data.attacks
        if attack is None:
            pool = [i for i in attacks
                    if all(j in [i.name for i in self.poke.types]
                           for j in attacks[i]["types"])
                    and attacks[i]["is_generic"]]
            full_pool = [i for i in self.poke.inf["attacks"] +
                         self.poke.inf["pool"] + pool
                         if i not in self.poke.attacks
                         and attacks[i]["min_lvl"] <= self.poke.lvl()]
            if len(full_pool) == 0:
                return False
            new_attack = random.choice(full_pool)
        else:
            new_attack = attack
        if ask_bool(self.map,
                    f"{self.poke.name} wants to learn \
{attacks[new_attack]['name']}!"):
            if len(self.poke.attacks) < 4:
                self.poke.attacks.append(new_attack)
                self.poke.attack_obs.append(Attack(new_attack,
                                                  len(self.poke.attacks)))
            else:
                self.box.add_c_obs([se.Text(f"{i + 1}: {j.name}", state="float")
                                    for i, j in enumerate(self.poke.attack_obs)])
                with self.box.center_add(self.map):
                    while True:
                        if _ev.get() in ["'s'", "'w'"]:
                            self.box.input(_ev.get())
                            self.map.show()
                            _ev.clear()
                        elif _ev.get() == "Key.enter":
                            i = self.box.index.index
                            self.poke.attacks[i] = new_attack
                            self.poke.attack_obs[i] = Attack(new_attack, i + 1)
                            _ev.clear()
                            ask_ok(self.map, f"{self.poke.name} learned \
{attacks[new_attack]['name']}!")
                            _ev.clear()
                            break
                        elif _ev.get() == "'1'":
                            _ev.clear()
                            Detail(self.map.height, self.map.width)\
                                  (self.poke, False)
                            self.map.show(init=True)
                        elif _ev.get() == "'2'":
                            with AttackInfo(attack, self.map):
                                easy_exit_loop()
                        elif _ev.get() in ["Key.esc", "'q'"]:
                            _ev.clear()
                            return False
                        std_loop()
                        time.sleep(0.05)
                self.box.remove_c_obs()
            return True
        return False


if __name__ == "__main__":
    print("\033[31;1mDo not execute this!\033[0m")
