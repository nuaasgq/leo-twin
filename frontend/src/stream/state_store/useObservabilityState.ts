import { useEffect, useState } from "react";

import { ObservabilityState, ObservabilityStore } from ".";

export function useObservabilityState(store: ObservabilityStore): ObservabilityState {
  const [state, setState] = useState<ObservabilityState>(() => store.getSnapshot());

  useEffect(() => store.subscribe(setState), [store]);

  return state;
}
