classdef baseclass < handle
% Base class and common functions for instruments and experiments

%==========================================================================
% PROPERTIES - CONSTANT
%==========================================================================
properties(Constant)
    hi      = 30;                           % pixel
    wi      = 90;                           % pixel
    ofx     = 10;                           % pixel
    ofy     = 10;                           % pixel
end


%==========================================================================
% PROPERTIES - VARIABLE
%==========================================================================
properties
    gui;
    dev;
    init = 0;
    stopping = 0;
    simulation = 0;
    data_to_save;
    busy = 0;
end


%==========================================================================
% FUNCTIONS - CONSTRUCTOR
%==========================================================================
methods

function obj = baseclass(vars)
    if length(vars) >= 1
        obj.dev = vars{1};
    else
        obj.dev = 1;
        obj.create_gui(0);
    end
end


%==========================================================================
% FUNCTIONS - ACTIONS
%==========================================================================
function create_gui(obj, position)
    panel_width  = obj.width * obj.wi + 2 * obj.ofx;
    panel_height = obj.height * obj.hi + 2 * obj.ofy + 10;
    if position == 0
        if ~isfield(obj.gui, 'id')
            obj.gui.id = -1;
        end
        if ~ishandle(obj.gui.id)  % do not redraw if exists
            obj.gui.id = str2double ([ num2str(obj.uid) ...
                                                num2str(obj.dev) ]);
            figure (obj.gui.id);
            set ( obj.gui.id, ...
                'Name', obj.title(),... %FIXME: obj.dev_* is uninitialized at this point
                'NumberTitle','off', ...
                'Menubar', 'none', ...
                'Toolbar', 'none', ...
                'Units', 'pixels' );
            position    = get ( obj.gui.id, 'Position');
            fig_width   = panel_width + 20;
            fig_height  = panel_height + 20;
            fig_x       = position(1) + position(3) - fig_width;
            fig_y       = position(2) + position(4) - fig_height;
            set (obj.gui.id, ...
                'Position', [fig_x fig_y fig_width fig_height], ...
                'Resize', 'off');
            clf  (obj.gui.id);
            zoom (obj.gui.id, 'on');
        else
            figure (obj.gui.id);
        end
        obj.gui.position = [ obj.gui.id 10 10 ];
    else
        obj.gui.position = position;
    end
    if ~isfield(obj.gui, 'uipanel')
        obj.gui.uipanel = -1;
    end
    if ~ishandle(obj.gui.uipanel)     % do not redraw if exists
        obj.gui.id    = obj.gui.position(1);
        h = uipanel ( obj.gui.id, ...
            'Title', obj.title(), ...
            'Units', 'pixels', ...
            'Position', [ obj.gui.position(2:end) ...
                          panel_width panel_height ], ...
            'UserData', obj.dev, ...
            'DeleteFcn', @obj.object_delete_fcn );
        obj.gui.uipanel = h;
        obj.draw_gui_controls;    
    end
end

function stop(obj)
    if obj.busy
        obj.gui_wait_show();
    end
    obj.stopping = 1;
end


%==========================================================================
% FUNCTIONS - GUI CALLBACKS
%==========================================================================
function object_delete_fcn(obj, ~, ~)
    obj.stop();
    obj.close();
end


function initialize_callback (obj, ~, ~)
    obj.gui.show = 1;
    obj.gui_wait_show();
    parent = obj.gui.uipanel;
    h = findobj (parent, 'Tag', 'Simulation');
    sim = get (h, 'Value');
    try
        obj.initialize(sim);
        obj.update();        
    catch e
        obj.init = 0;
        fprintf(2,'%s\n%s\n',e.identifier, e.message);
    end
    obj.update_initialization_status();
    drawnow;
    obj.gui_wait_delete();
end


function close_callback(obj, ~, ~)
    obj.stop();
    obj.gui_wait_show();
    try
        obj.close();
    catch
        obj.disp_msg([obj.title() ' closing failed']);
    end
    obj.update_initialization_status ();
    drawnow;
    obj.gui_wait_delete();
end


function stop_callback(obj, ~, ~)
    obj.stop()
end

function for_save_callback (~, ~,~)
    [h, h_fig]  = gcbo;
    h_all       = findobj (h_fig, '-regexp', 'Tag', 'for_save*');
    h_uncheck   = setxor (h_all,h);
    set (h_uncheck, 'Value', 0);
end


%==========================================================================
% FUNCTIONS - LOW LEVEL
%==========================================================================
function update_initialization_status(obj)
    parent  = obj.gui.uipanel;
    h       = findobj (parent, 'Tag', 'initialization_status');
    if obj.init == 1
        set (h, 'BackgroundColor', 'green', 'String', 'ON' );
    else
        set (h, 'BackgroundColor', 'red', 'String', 'OFF' );
    end
end


function gui_wait_show(obj)
    if obj.gui.show
        h = uicontrol ('Parent', obj.gui.uipanel, ...
            'style','pushbutton', ...
            'enable', 'inactive', ...
            'units', 'normalized', ...
            'position', [.125 .30 .75 .40], ...
            'FontUnits', 'normalized', ...
            'FontSize', .3, ...
            'FontWeight', 'bold', ...
            'ForegroundColor', 'yellow', ...
            'BackgroundColor', 'black', ...
            'String', 'Busy...', ...
            'Callback', '');
        obj.gui.wait.id = h;
        drawnow
    end
end


function gui_wait_delete(obj)
    if obj.gui.show
        delete (obj.gui.wait.id);
        drawnow
    end
end


function prepare_save(obj, ax)
    h_panel     = obj.gui.uipanel;
    h_save      = findobj (h_panel, 'Tag', 'for_save');
    d.h_axes    = ax;
    d.data      = obj.data_to_save;
    set (h_save, 'UserData', d);
end


end % methods


%==========================================================================
% FUNCTIONS - STATIC HELPER FUNCTIONS
%==========================================================================
methods(Static)
   
function disp_msg(msg)
    disp ([ mfilename '.m: ' msg]);
    msg_end = ' ';
    if length(msg)>3
        if strcmpi (msg(end-2:end),'...')
            msg_end = '';
        end
    end
    disp (msg_end);
end


function h = draw_buttongroup ( parent, position, callback )
    h = uibuttongroup ( 'Parent', parent, ...
                        'Units', 'pixels', ...
                        'Position', position, ...
                        'SelectionChangeFcn', callback);
end


function h = draw_pushbutton ( parent, position, label, callback )
    h = uicontrol ( 'Parent', parent, 'Style', 'pushbutton', ...
                    'FontUnits', 'normalized', ...
                    'FontSize', .4, ...
                    'Position', position, ...
                    'Callback', callback, ...
                    'String', label);
end


function h = draw_edit ( parent, position, tag, value )
    h = uicontrol ( 'Parent', parent, 'Style', 'edit', ...
                    'FontUnits', 'normalized', ...
                    'FontSize', .4, ...
                    'Position', position, ...
                    'Tag', tag, ...
                    'String', value);
end


function h = draw_radio ( parent, position, label, userData )
    h = uicontrol ( 'Parent', parent, 'Style', 'radio', ...
                    'FontUnits', 'normalized', ...
                    'FontSize', .4, ...
                    'Position', position, ...
                    'String', label, ...
                    'UserData', userData);            
end


function h = draw_label ( parent, position, label )
    h = uicontrol ( 'Parent', parent, ...
                    'Style', 'text', ...
                    'String', label, ...
                    'Position', position);
end


function h = draw_axes (parent, position )
    h = axes ('Parent', parent, ...
              'Units', 'pixels', ...
              'Position', position);
end


function h = draw_panel (parent, position, title )
    h = uipanel ('Parent', parent, ...
                 'Units', 'pixels', ...
                 'Position', position, ...
                 'Title', title);
end


function h = draw_checkbox(parent, position, label, value, tag, callback)
    h = uicontrol ( 'Parent', parent, 'Style', 'checkbox', ...
                    'FontUnits', 'normalized', ...
                    'FontSize', .4, ...
                    'position', position, ...
                    'String', label, ...
                    'Value', value, ...
                    'Tag', tag, ...
                    'Callback', callback);
end

end % methods
end % classdef