#!/usr/bin/env python3
"""Roll back EventInstanceManager objects leaked by failed event setup scripts."""

from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src/main/java/scripting/event/EventManager.java"
text = path.read_text(encoding="utf-8")

old = '''    private EventInstanceManager createInstance(String name, Object... args) throws ScriptException, NoSuchMethodException {
        return (EventInstanceManager) iv.invokeFunction(name, args);
    }
'''
new = '''    private void rollbackFailedSetup(Set<String> existingInstanceNames) {
        List<EventInstanceManager> leakedInstances = new ArrayList<>();
        synchronized (instances) {
            Iterator<Map.Entry<String, EventInstanceManager>> iterator = instances.entrySet().iterator();
            while (iterator.hasNext()) {
                Map.Entry<String, EventInstanceManager> entry = iterator.next();
                if (!existingInstanceNames.contains(entry.getKey())) {
                    leakedInstances.add(entry.getValue());
                    iterator.remove();
                }
            }
        }

        for (EventInstanceManager leaked : leakedInstances) {
            leaked.dispose(true);
        }
    }

    private EventInstanceManager createInstance(String name, Object... args) throws ScriptException, NoSuchMethodException {
        Set<String> existingInstanceNames;
        synchronized (instances) {
            existingInstanceNames = new HashSet<>(instances.keySet());
        }

        try {
            EventInstanceManager created = (EventInstanceManager) iv.invokeFunction(name, args);
            if (created == null) {
                rollbackFailedSetup(existingInstanceNames);
            }
            return created;
        } catch (ScriptException | NoSuchMethodException ex) {
            rollbackFailedSetup(existingInstanceNames);
            throw ex;
        }
    }
'''

if new in text:
    print("Boss/PQ failed-setup rollback already applied.")
elif text.count(old) == 1:
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("Applied Boss/PQ failed-setup rollback.")
else:
    raise SystemExit(f"Expected one EventManager.createInstance source block, found {text.count(old)}")
