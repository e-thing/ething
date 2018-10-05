const LAYOUT_HORIZONTAL = 'horizontal';
const LAYOUT_VERTICAL = 'vertical';

export default {
  name: 'multipane',

  props: {
    layout: {
      type: String,
      default: LAYOUT_VERTICAL,
    },
  },

  data() {
    return {
      isResizing: false,
    };
  },

  computed: {
    classnames() {
      return [
        'multipane',
        'layout-' + this.layout.slice(0, 1),
        this.isResizing ? 'is-resizing' : '',
      ];
    },
    cursor() {
      return this.isResizing
        ? this.layout == LAYOUT_VERTICAL ? 'col-resize' : 'row-resize'
        : '';
    },
    userSelect() {
      return this.isResizing ? 'none' : '';
    },
  },

  methods: {
    onMouseDown(e) {
      let resizer = e.target;
      if (resizer.className && resizer.className.match('multipane-resizer')) {

        function getPageAttr (e, coord) {
          var name = 'page' + coord
          if (typeof e[name] === 'number')
            return e[name]
          if (e.touches && e.touches.length>0)
            return e.touches[0][name]
        }

        e.preventDefault();
        let initialPageX = getPageAttr(e, 'X');
        let initialPageY = getPageAttr(e, 'Y');
        let self = this;
        let { $el: container, layout } = self;

        let reversed = Boolean(resizer.className.match('affect-follower'))

        let pane = resizer.previousElementSibling;
        if (reversed) {
          pane = resizer.nextElementSibling;
        }
        let {
          offsetWidth: initialPaneWidth,
          offsetHeight: initialPaneHeight,
        } = pane;

        let usePercentage = !!(pane.style.width + '').match('%');

        const { addEventListener, removeEventListener } = window;

        const resize = (initialSize, offset = 0) => {
          if (reversed) {
            offset = -offset;
          }
          if (layout == LAYOUT_VERTICAL) {
            let containerWidth = container.clientWidth;
            let paneWidth = initialSize + offset;

            return (pane.style.width = usePercentage
              ? paneWidth / containerWidth * 100 + '%'
              : paneWidth + 'px');
          }

          if (layout == LAYOUT_HORIZONTAL) {
            let containerHeight = container.clientHeight;
            let paneHeight = initialSize + offset;

            return (pane.style.height = usePercentage
              ? paneHeight / containerHeight * 100 + '%'
              : paneHeight + 'px');
          }
        };

        // This adds is-resizing class to container
        self.isResizing = true;

        // Resize once to get current computed size
        let size = resize();

        // Trigger paneResizeStart event
        self.$emit('paneResizeStart', pane, resizer, size);

        const onMouseMove = function(e) {
          //e.preventDefault();
          let pageX = getPageAttr(e, 'X');
          let pageY = getPageAttr(e, 'Y');
          size =
            layout == LAYOUT_VERTICAL
              ? resize(initialPaneWidth, pageX - initialPageX)
              : resize(initialPaneHeight, pageY - initialPageY);

          self.$emit('paneResize', pane, resizer, size);
        };

        const onMouseUp = function() {
          // Run resize one more time to set computed width/height.
          size =
            layout == LAYOUT_VERTICAL
              ? resize(pane.clientWidth)
              : resize(pane.clientHeight);

          // This removes is-resizing class to container
          self.isResizing = false;

          removeEventListener('mousemove', onMouseMove);
          removeEventListener('mouseup', onMouseUp);
          removeEventListener('touchmove', onMouseMove);
          removeEventListener('touchend', onMouseUp);

          self.$emit('paneResizeStop', pane, resizer, size);
        };

        addEventListener('mousemove', onMouseMove);
        addEventListener('mouseup', onMouseUp);
        addEventListener('touchmove', onMouseMove);
        addEventListener('touchend', onMouseUp);
      }
    },
  },
};
