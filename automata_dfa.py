"""Simple DFA implementation used by the GUI simulator.

Provides a deterministic finite automaton (DFA) class with a small,
clear API used by the GUI. The implementation keeps the transition
function total by optionally adding a dead state. The class is
lightweight and intentionally dependency-free (pure Python).

Author: generated for user
"""

from typing import Dict, Set, Optional, Iterable, Tuple


class DFA:
	"""Deterministic Finite Automaton.

	States are arbitrary hashable values (commonly strings).

	Usage (minimal):
		dfa = DFA(states={'q0','q1'}, alphabet={'a','b'},
				  delta={'q0':{'a':'q1','b':'q0'}, 'q1':{'a':'q1','b':'q0'}},
				  start='q0', accept={'q1'})
		dfa.accepts('abba')
	"""

	DEAD = "__DEAD__"

	def __init__(self,
				 states: Optional[Iterable[str]] = None,
				 alphabet: Optional[Iterable[str]] = None,
				 delta: Optional[Dict[str, Dict[str, str]]] = None,
				 start: Optional[str] = None,
				 accept: Optional[Iterable[str]] = None,
				 make_total: bool = True):
		self.states: Set[str] = set(states or [])
		self.alphabet: Set[str] = set(alphabet or [])
		self.delta: Dict[str, Dict[str, str]] = {}
		self.start = start
		self.accept: Set[str] = set(accept or [])
		self.current: Optional[str] = None

		# Copy transitions defensively
		if delta:
			for s, trans in delta.items():
				self.delta[s] = dict(trans)
				self.states.add(s)

		# add any states that appear as targets
		for s_map in list(self.delta.values()):
			for tgt in s_map.values():
				self.states.add(tgt)

		if make_total:
			self._make_total()

		# initialize current state
		self.reset()

	# --- construction helpers -------------------------------------------------
	def add_state(self, name: str, is_accept: bool = False) -> None:
		self.states.add(name)
		if is_accept:
			self.accept.add(name)

	def add_transition(self, src: str, symbol: str, tgt: str) -> None:
		self.states.add(src)
		self.states.add(tgt)
		self.alphabet.add(symbol)
		self.delta.setdefault(src, {})[symbol] = tgt

	def _make_total(self) -> None:
		"""Ensure delta is total by adding a dead state and missing transitions.

		Important: iterate over a static snapshot to avoid mutating a set
		during iteration (which would raise RuntimeError).
		"""
		# ensure every state has at least an entry in delta
		for s in list(self.states):
			self.delta.setdefault(s, {})

		# if alphabet is empty, nothing to do
		if not self.alphabet:
			return

		# Add dead state only if some transition is missing
		need_dead = False
		for s in list(self.states):
			for a in self.alphabet:
				if a not in self.delta.get(s, {}):
					need_dead = True
					break
			if need_dead:
				break

		if need_dead:
			dead = DFA.DEAD
			self.states.add(dead)
			# dead loops to itself on every symbol
			self.delta.setdefault(dead, {})
			for a in self.alphabet:
				self.delta[dead].setdefault(a, dead)

			# fill missing transitions to dead
			for s in list(self.states):
				for a in self.alphabet:
					self.delta.setdefault(s, {}).setdefault(a, dead)

	# --- simulation -----------------------------------------------------------
	def reset(self) -> None:
		self.current = self.start

	def step(self, symbol: str) -> Optional[str]:
		"""Consume one input symbol and update the current state.

		Returns the new current state, or None if symbol not in alphabet
		or if the DFA is not properly configured.
		"""
		if symbol not in self.alphabet:
			return None
		if self.current is None:
			return None
		self.current = self.delta.get(self.current, {}).get(symbol)
		return self.current

	def run(self, w: Iterable[str]) -> Optional[str]:
		"""Run the DFA on the input iterable `w` (sequence of symbols).

		Returns the final state, or None on invalid input.
		"""
		self.reset()
		for ch in w:
			if ch not in self.alphabet:
				return None
			self.step(ch)
		return self.current

	def accepts(self, w: Iterable[str]) -> Optional[bool]:
		"""Return True/False whether `w` is accepted, or None if invalid.

		None is returned when the input contains symbols not in alphabet.
		"""
		final = self.run(w)
		if final is None:
			return None
		return final in self.accept

	# --- utilities ------------------------------------------------------------
	def to_dict(self) -> Dict:
		return {
			'states': sorted(self.states),
			'alphabet': sorted(self.alphabet),
			'delta': {s: dict(self.delta.get(s, {})) for s in sorted(self.states)},
			'start': self.start,
			'accept': sorted(self.accept),
		}

	@classmethod
	def from_components(cls, states, alphabet, delta, start, accept):
		return cls(states=states, alphabet=alphabet, delta=delta, start=start, accept=accept)

	def __repr__(self) -> str:
		return f"DFA(start={self.start!r}, states={sorted(self.states)!r}, accept={sorted(self.accept)!r})"


def example_ends_with_ab() -> DFA:
	"""Return a small DFA accepting strings over {a,b} that end with 'ab'."""
	states = {'q0', 'q1', 'q2'}
	alphabet = {'a', 'b'}
	delta = {
		'q0': {'a': 'q1', 'b': 'q0'},
		'q1': {'a': 'q1', 'b': 'q2'},
		'q2': {'a': 'q1', 'b': 'q0'},
	}
	start = 'q0'
	accept = {'q2'}
	return DFA(states=states, alphabet=alphabet, delta=delta, start=start, accept=accept)


if __name__ == '__main__':
	# quick command-line sanity demo
	dfa = example_ends_with_ab()
	tests = ['ab', 'aab', 'aba', 'b', '']
	for t in tests:
		res = dfa.accepts(t)
		print(f"{t!r}: {res}")
