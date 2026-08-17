import { useEffect, useRef } from "react";

// The little menu a row hangs off. It is fixed rather than absolute because the sidebar scrolls, and
// an absolute menu would be clipped by the very list it belongs to.
//
// It registers no key listener: Escape belongs to App's one listener, the same rule ConfirmDialog
// follows, so the order of what closes first stays in a single place. A click elsewhere is the
// menu's own event and is handled here.

export default function RowMenu({ items, onClose }) {
  const menu = useRef(null);

  useEffect(() => {
    const onDown = (event) => {
      if (!menu.current?.contains(event.target)) onClose?.();
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, [onClose]);

  return (
    <div className="row-menu" ref={menu}>
      {items.map((item) => (
        <button
          key={item.label}
          type="button"
          className={item.danger ? "row-menu__item row-menu__item--danger" : "row-menu__item"}
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
  );
}
