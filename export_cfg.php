<?php
define('CLI_SCRIPT', true);
require('config.php');
require('lib/clilib.php');

$usage = "
php export_cfg.php --all
Export the config for Moodle core components and the plugins.

php export_cfg.php --plugins
Export the config for the plugins.

php export_cfg.php --component=xxx
Export the config for this particular component.

php export_cfg.php --all > settings.conf
On Linux use the > operator to redirect the output to a file.
";

list($options, $unrecognized) = cli_get_params(
    [
        'all' => false,
        'component' => false,
        'help' => false,
        'plugins' =>false
    ],
    ['h' => 'help']
);

// If no param is passed or help is requested.
if (($options['component'] === false && $options['plugins'] === false && $options['all'] === false) || ($options['help'])) {
    exit($usage);
}

// Process the passed parameter.
if ($options['all']) {
    $components = get_config_plugins('core');
}

if ($options['plugins']) {
    $components = get_config_plugins();
}

if ($options['component']) {
    if (strpos($options['component'], ',') !== false) {
        $components = explode(',', $options['component']);
    } else {
        $components = array($options['component']);
    }
}

///////////////////////////////////////////
///////////// S E T T I N G S /////////////

// PHP localtion.
$php = '/usr/bin/php';

// Exit code.
$status = -1;
///////////////////////////////////////////

// Contains all the commands to output.
$output = '';

if (is_array($components)) {
    foreach($components as $value) {
        $output .= output_settings($value);
    }
}

echo $output;

function output_settings($component) {
    global $php, $status;

    // Contains the output of the cfg.php
    $cmdLineOutput = array();

    // Contains the individual PHP commands.
    $commands = '';

    // Get the cfg.php Moodle script to output the component settings in JSON format.
    // We export the settings in JSON so it is easier to manage the multi-line settings.
    exec($php.' admin/cli/cfg.php --component='.$component.' --json', $cmdLineOutput, $status);

    if ($status === 0) {

        $objCmdLineOutput = json_decode($cmdLineOutput[0]);

        // Do not print the component if it only has a version setting and no other settings.
        if (count(get_object_vars($objCmdLineOutput)) == 1 && isset($objCmdLineOutput->version)) {
            return "";
        }

        // Make sure the incoming and the local components are at the same version.
        // $localVersion = $DB->get_record('config_plugins', ['plugin' => $component, 'name' => 'version']);
        // if ($localVersion->version == $objCmdLineOutput->version) {
        //     return "";
        // }

        foreach ($objCmdLineOutput as $name => $set) {
            $commands .= sprintf(
                "%s admin/cli/cfg.php --component=%s --name=%s --set=%s\n",
                $php, $component, $name, escapeshellarg($set)
            );
        }
    }

    return $commands;
}

function get_config_plugins($extra = false) {
    global $CFG, $DB;

    if ($extra !== false) {
        $components[] = $extra;
    }

    $plugins = $DB->get_records_sql("SELECT * FROM {$CFG->prefix}config_plugins GROUP BY plugin");
    foreach ($plugins as $plugin) {
        $components[] = $plugin->plugin;
    }

    return $components;
}
