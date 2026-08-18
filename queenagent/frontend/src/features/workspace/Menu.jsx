import { useLayoutEffect, useRef, useState } from "react";

import { placeMenu } from "../../shared/menuPlacement.js";

// The one popup box in the app: the sidebar row's ⋯ menu today, the model and Skills menus from
// Madde 26 and 27. What is shared is where it goes, how tall it may get and how it is dismissed;
// the width belongs to each caller, so this box does not set one.
//
// It is fixed rather than absolute because the sidebar scrolls, and an absolute menu would be
// clipped by the very list it belongs to. The placement is therefore measured against the window,
// which is only knowable after the box exists -- hence the layout effect.
//
// It registers no key listener: Escape belongs to App's one listener, the same rule ConfirmDialog
// follows, so the order of what closes first stays in a single place.

export default function Menu({ items, anchor, onClose }) {
  const menu = useRef(null);
  const [place, setPlace] = useState(null);

  useLayoutEffect(() => {
    if (!anchor || !menu.current) return;
    setPlace(
      placeMenu(anchor.getBoundingClientRect(), menu.current.getBoundingClientRect(), {
        width: window.innerWidth,
        height: window.innerHeight,
      }),
    );
  }, [anchor]);

  return (
    <>
      {/* A catcher, not a listener on the document: this way the click that dismisses the menu is
          spent on dismissing it and does not also press what was underneath. */}
      <div className="menu__catcher" data-testid="menu-catcher" onClick={() => onClose?.()} />
      <div
        className="menu"
        ref={menu}
        style={place ? { left: place.left, top: place.top, maxHeight: place.maxHeight } : undefined}
      >
        {items.map((item) => (
          <button
            key={item.label}
            type="button"
            className={item.danger ? "menu__item menu__item--danger" : "menu__item"}
            title={item.danger ? item.label : undefined}
            onClick={() => {
              item.onChoose?.();
              onClose?.();
            }}
          >
            {item.label}
          </button>
        ))}
      </div>
    </>
  );
}
