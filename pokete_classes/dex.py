"""Contains the Pokete dex that gives information about all Poketes"""

import time
import scrap_engine as se
import pokete_data as p_data
from pokete_general_use_fns import liner, easy_exit_loop, std_loop
from .poke import Poke
from .event import _ev
from .ui_elements import ChooseBox, Box


class Dex:
    """The Pokete dex that shows stats about all Poketes ever caught
    ARGS:
        _map: se.Map this will be shown on"""

    def __init__(self, _map, figure):
        self.box = ChooseBox(_map.height - 3, 35, "Poketedex")
        self.detail_box = Box(16, 35)
        self.figure = figure
        self.map = _map
        self.idx = 0
        self.obs = []
        self.detail_info = se.Text("", state="float")
        self.detail_desc = se.Text("", state="float")
        self.detail_box.add_ob(self.detail_info, 16, 1)
        self.detail_box.add_ob(self.detail_desc, 3, 7)

    def add_c_obs(self):
        """Adds c_obs to box"""
        self.box.add_c_obs(self.obs[self.idx * (self.box.height - 2):
                                    (self.idx + 1) * (self.box.height - 2)])

    def rem_c_obs(self):
        """Removes c_obs to box"""
        for c_ob in self.box.c_obs:
            c_ob.remove()
        self.box.remove_c_obs()

    def detail(self, poke):
        """Shows details about the Pokete
        ARGS:
            poke: Pokes identifier"""
        _ev.clear()
        poke = Poke(poke, 0)
        desc_text = liner(poke.desc.text.replace("\n", " ") +
                          (f"""\n\n Evolves to {
                              p_data.pokes[poke.evolve_poke]['name'] if
                              poke.evolve_poke in
                              self.figure.caught_pokes else '???'
                                                }."""
                           if poke.evolve_lvl != 0 else ""), 29)
        self.detail_box.resize(9 + len(desc_text.split("\n")), 35)
        self.detail_box.name_label.rechar(poke.name)
        self.detail_box.add_ob(poke.ico, 3, 2)
        self.detail_desc.rechar(desc_text)
        self.detail_info.rechar("Type: ")
        self.detail_info += se.Text(poke.type.name.capitalize(),
                                    esccode=poke.type.color) + se.Text((f"""
HP: {poke.hp}
Attack: {poke.atc}
Defense: {poke.defense}
Initiative: {poke.initiative}"""))
        with self.detail_box.center_add(self.map):
            easy_exit_loop()
        self.detail_box.rem_ob(poke.ico)

    def __call__(self):
        """Opens the dex"""
        pokes = p_data.pokes
        _ev.clear()
        self.idx = 0
        p_dict = {i[1]: i[-1] for i in
                  sorted([(pokes[j]["types"][0], j, pokes[j])
                          for j in list(pokes)[1:]])}
        self.obs = [se.Text(f"{i + 1} \
{p_dict[poke]['name'] if poke in self.figure.caught_pokes else '???'}",
                    state="float")
                    for i, poke in enumerate(p_dict)]
        self.add_c_obs()
        with self.box.add(self.map, self.map.width - self.box.width, 0):
            while True:
                for event, idx, n_idx, add, idx_2 in zip(
                                ["'s'", "'w'"],
                                [len(self.box.c_obs) - 1, 0],
                                [0, self.box.height - 3], [1, -1], [-1, 0]):
                    if _ev.get() == event and self.box.index.index == idx:
                        if self.box.c_obs[self.box.index.index]\
                                    != self.obs[idx_2]:
                            self.rem_c_obs()
                            self.idx += add
                            self.add_c_obs()
                            self.box.set_index(n_idx)
                        _ev.clear()
                if _ev.get() == "Key.enter":
                    if "???" not in self.box.c_obs[self.box.index.index].text:
                        self.detail(list(p_dict)[self.idx
                                                 * (self.box.height - 2)
                                                 + self.box.index.index])
                    _ev.clear()
                elif _ev.get() in ["'s'", "'w'"]:
                    self.box.input(_ev.get())
                    _ev.clear()
                elif _ev.get() in ["'e'", "Key.esc", "'q'"]:
                    _ev.clear()
                    break
                std_loop()
                time.sleep(0.05)
                self.map.show()
            self.rem_c_obs()
