classdef Rb_Controller < baseclass
% Template for creating new instruments and experiments %TODO
% John Smith, September 2017 %TODO

%==========================================================================
% PROPERTIES - CONSTANT
%==========================================================================
properties(Constant)
    uid = 0; %TODO
    height = 9;
    width  = 8;
    ip_self = '192.168.137.1';
    ip_RPi = '192.168.137.132';
    usrname = 'pi';
    psswrd = 'rbcontroller';
    port = 4000;
    timeout = 10;
end


%==========================================================================
% PROPERTIES - VARIABLES
%==========================================================================
properties
    tcp_server % Description
    timeVal = 0;
    time = [];
    temperature = [];
    plot_length = 1;
    output_off = false;
    output_pause = false;
    frequency = 2;
end


%==========================================================================
% FUNCTIONS - CONSTRUCTOR
%==========================================================================
methods

function obj = Rb_Controller(varargin) %TODO
    obj@baseclass(varargin);
end


function title = title(obj)
    title = [ 'Rb Controller ' num2str(obj.dev) ' - MATLAB UI for Raspberry Pi' ]; % TODO
end


%==========================================================================
% FUNCTIONS - ACTIONS
%==========================================================================
function initialize(obj, sim)
    if obj.init == 1
        obj.disp_msg('Already initialized');
    else
        obj.simulation = sim;
        if ~obj.simulation
            %obj.tcp_server = tcpserver(obj.ip_self,obj.port,'ConnectionChangedFcn',@obj.connectionFcn,'Timeout',obj.timeout);
            %obj.tcp_server = tcpserver('localhost',obj.port,'ConnectionChangedFcn',@obj.connectionFcn,'Timeout',obj.timeout);
            obj.tcp_server = tcpserver(obj.port,'ConnectionChangedFcn',@obj.connectionFcn,'Timeout',obj.timeout);
            configureCallback(obj.tcp_server,"terminator",@obj.receiveMsg);
            obj.busy = 1;
        else
            obj.init = 1;
        end
        %obj.init = 1; % The system is only initialized once the Raspberry
        %Pi has connected to the server AND has connected to the PSU and LucidCtrl device. The init parameter is set in the
        %callback function 'receiveMsg()'
        obj.busy = 1;
        obj.init = 0;
        obj.stopping = 0;
    end
end

function update(obj)
    if ~obj.simulation
        %TODO
    end
end

function close(obj)
    if obj.init == 1
        if ~obj.simulation
            try
                obj.stop_program();
            catch e
                obj.disp_msg(['RB Controller ' num2str(obj.dev) ' closing failed']);
            end
        end
        obj.init = 0;
        clear obj.tcp_server;
        obj.gui_wait_delete();
    end
end

function stop_program(obj)
    if ~obj.simulation
        L = 's';
        write(obj.tcp_server,L);
    end
end    

function off(obj)
    if ~obj.simulation
        L = 'o';
        write(obj.tcp_server,L);
    end
end

function setT(obj,T)
    if ~obj.simulation
        L = strcat("t ",string(T));
        write(obj.tcp_server,L);
    end
end

function pause(obj)
    if ~obj.simulation
        L = 'p';
        write(obj.tcp_server,L);
    end
end

% This callback for the tcp server handles all incoming packets from the
% Raspberry Pi controller
function receiveMsg(obj,src,~)
    parent  = obj.gui.uipanel;
    msg = readline(src);
    if strcmp(msg,"CONNECTED")
        obj.disp_msg(msg);
        obj.busy = 0;
        obj.init = 1;
        obj.update_initialization_status();
    elseif strcmp(msg,"READY")
        h = findobj(parent, 'Tag', 'actual_temperature');
        set (h, 'BackgroundColor', 'green');
    elseif strcmp(msg,"NOT_READY")
        h = findobj(parent, 'Tag', 'actual_temperature');
        set (h, 'BackgroundColor', 'red');        
    elseif strcmp(msg,"TARGET_CHANGED")
        h = findobj (parent, 'Tag', 'set_temperature');
        set (h, 'String', double(readline(src)));
    elseif strcmp(msg,"AVG_TEMP")
        obj.timeVal = obj.timeVal + 1/obj.frequency;
        obj.time = [obj.time obj.timeVal];
        obj.temperature = [obj.temperature double(readline(src))];
        obj.time = obj.time(max(1,length(obj.time) - obj.frequency * obj.plot_length):length(obj.time));
        obj.temperature = obj.temperature(max(1,length(obj.temperature) - obj.frequency * obj.plot_length):length(obj.temperature));
        h = findobj (parent, 'Tag', 'actual_temperature');
        set(h, 'String', obj.temperature(length(obj.temperature)));
        obj.update_plot()
    end
end

function connectionFcn(obj,src,~)
    parent  = obj.gui.uipanel;
    h = findobj(parent, 'Tag', 'actual_temperature');
    if src.Connected
        obj.disp_msg("This message is sent by the server after accepting the client connection request");
    else
        set(h, 'BackgroundColor', 'red');
        obj.disp_msg("Client has disconnected");
        obj.init = 0;
        obj.update_initialization_status()
        set(h, 'String', '-999.99');
    end
end

function update_plot(obj)
    h_axes  = obj.gui.axis.id;
    xdata = obj.time;
    ydata = obj.temperature;
    h_line  = get(h_axes, 'children');
    set(h_line, 'xdata', xdata, 'ydata', ydata);
end

%==========================================================================
% FUNCTIONS - LOW LEVEL
%==========================================================================
function draw_gui_controls(obj)
    parent  = obj.gui.uipanel;

    % initialize
    obj.draw_checkbox(parent, ...
            [ obj.ofx 1*obj.ofy+2*obj.hi obj.wi obj.hi], ...
            'Simulation', 0, 'Simulation', '');
    h = obj.draw_edit(parent, ...
            [ obj.ofx obj.ofy 2*obj.wi obj.hi], ...
            'initialization_status', '');
    set (h, 'BackgroundColor', 'red', ...
            'FontWeight', 'bold', ...
            'String', 'OFF', ...
            'Enable', 'inactive',...
            'Callback', '');
    obj.draw_pushbutton( parent, ...
            [ obj.ofx obj.ofy+obj.hi obj.wi obj.hi], ...
            'Initialize', @obj.initialize_callback);
    obj.draw_pushbutton( parent, ...
            [ obj.ofx+obj.wi obj.ofy+obj.hi obj.wi obj.hi], ...
            'Close', @obj.close_callback);
        
    % Save
    obj.draw_checkbox (parent, ...
            [obj.ofx+obj.wi 1*obj.ofy+2*obj.hi obj.wi obj.hi], ...
           'Save', ...
           0, ...
           'for_save', ...
           @obj.for_save_callback);
       
    % Off
    h = obj.draw_checkbox(parent, ...
           [obj.ofx obj.ofy+7*obj.hi obj.wi 2*obj.hi], ...
           'Output Off', 0, 'output_off', @obj.off_callback);
    set(h, 'FontSize', .2)
    
    % Pause
    h = obj.draw_checkbox( parent, ...
           [obj.ofx+obj.wi obj.ofy+7*obj.hi obj.wi 2*obj.hi], ...
           'Pause output', 0, 'pause_output', @obj.pause_callback);
    set(h, 'FontSize', .2)
    
    % Set temperature
    obj.draw_edit ( parent, ...
           [ obj.ofx+2*obj.wi obj.ofy+3*obj.hi obj.wi 2*obj.hi], ...
           'set_temperature', ...
           '1');
    h = obj.draw_pushbutton( parent, ...
           [ obj.ofx+2*obj.wi obj.ofy+5*obj.hi obj.wi 2*obj.hi], ...
           'Set temperature', @obj.set_temp_callback);
    set(h, 'FontSize', .2)
       
    % measure
    h = axes ( 'parent', parent, 'units', 'pixels', ...
               'position', [ obj.ofx+(obj.width - 4.5)*obj.wi obj.ofy+obj.hi 4.5*obj.wi 6*obj.hi], ...
               'box', 'on');
    obj.gui.axis.id = h;
    line(1, 1, 'parent', h);
    xlabel(h, 'Time [s]');
    ylabel(h, 'Temperature [C]');
    title(h, '','Interpreter','none');
    
    % Actual temperature
    h = obj.draw_edit ( parent, ...
               [obj.ofx+4.75*obj.wi obj.ofy+7*obj.hi 2*obj.wi 2*obj.hi], ...
               'actual_temperature', ...
               '-999.99');
    set (h, 'FontSize', .6, ...
            'BackgroundColor', 'red', ...
            'FontWeight', 'bold', ...
            'Enable', 'inactive',...
            'Callback', '');
        
    % Choose plot length
    obj.draw_edit ( parent, ...
           [obj.ofx+7*obj.wi obj.ofy+7*obj.hi obj.wi obj.hi], ...
           'plot_length', ...
           '1');
    h = obj.draw_pushbutton( parent, ...
           [obj.ofx+7*obj.wi obj.ofy+8*obj.hi obj.wi obj.hi], ...
           'Apply plot length [s]', @obj.plot_length_callback);
    set(h, 'FontSize', .32)
end


%==========================================================================
% FUNCTIONS - GUI CALLBACKS
%==========================================================================

function off_callback(obj, ~, ~)
    obj.off();
end

function pause_callback(obj, ~, ~)
    obj.pause();
end

function set_temp_callback (obj, ~,~)
    parent  = obj.gui.uipanel;
    h = findobj(parent, 'Tag', 'set_temperature');
    obj.setT(str2double(get(h,'string')));
end

function plot_length_callback (obj, ~,~)
    parent  = obj.gui.uipanel;
    h = findobj(parent, 'Tag', 'plot_length');
    obj.plot_length = str2double(get(h,'string'));
end

end % methods
end % classdef