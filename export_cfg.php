<?php
define('CLI_SCRIPT', true);
require('config.php');
require('lib/clilib.php');

$usage = "

php export_cfg.php --all
Export the config for Moodle core components and the plugins.
Can easily go up to 3,000 commands. You may want to > it into a file.

php export_cfg.php --plugins
Export the config for the plugins.

php export_cfg.php --component=xxx
Export the config for this particular component.

php export_cfg.php --all > settings.conf
On Linux, use the > operator to redirect the output to a file.


";

list($options, $unrecognized) = cli_get_params(
    [
        'all' => false,
        'component' => false,
        'help' => false,
        'plugins' =>false,
        'verbose' => false
    ],
    ['h' => 'help', 'v' => 'verbose', 'a' => 'all']
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
    $totalComponents = count($components);
    foreach($components as $key => $value) {
        $output .= output_settings($value, $key, $totalComponents);
    }
}

echo $output;

function output_settings($component, $index, $totalComponents) {
    global $php, $options, $status;

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

            // Alert user that the module is skipped.
            if ($options['verbose']) {
                // Output the component being exported when in verbose mode.
                cli_writeln('Skipping : ('.$index.'/'.$totalComponents.') ' . $component, STDERR);
            }

            return "";
        }

        // Make sure the incoming and the local components are at the same version.
        // $localVersion = $DB->get_record('config_plugins', ['plugin' => $component, 'name' => 'version']);
        // if ($localVersion->version == $objCmdLineOutput->version) {
        //     return "";
        // }

        $settingsToIgnore = array(
            // Core
            'siteidentifier', 'supportemail', 'siteadmins', 'themerev', 'jsrev', 'langrev', 'localcachedirpurged', 'scheduledtaskreset', 'allversionshash',
            'fileslastcleanup', 'digestmailtimelast', 'scorm_updatetimelast', 'templaterev', 'noemailever', 'auth', 'enrol_plugins_enabled',
            'cronremotepassword', 'secretphrase', 'recaptchapublickey', 'recaptchaprivatekey', 'allowedip', 'blockedip',
            // Core - database
            'dbtype', 'dblibrary', 'dbhost', 'dbname', 'dbuser', 'dbpass', 'prefix', 'wwwroot',
            // Core - file permissions
            'directorypermissions', 'dirroot', 'filepermissions', 'umaskpermissions',
            // Core - path
            'dataroot', 'libdir', 'tempdir', 'backuptempdir', 'cachedir', 'localcachedir', 'localrequestdir', 'langotherroot', 'langlocalroot',
            'noreplyaddress', 'chat_serverhost', 'pathtogs', 'geoip2file', 'auth_instructions',
            // Core - OS path
            'pathtounoconv',
            // Core - SMTP
            'smtphosts', 'smtpsecure', 'smtpauthtype', 'smtpuser', 'smtppass', 'smtpmaxbulk', 'proxypassword',
            // Cookie
            'sessioncookie','sessioncookiepath', 'sessioncookiedomain',
            // mod_lti
            'kid', 'privatekey',
            // filter_tex
            'pathconvert', 'pathdvips', 'pathdvisvgm', 'pathlatex',
            // Poodll user and secret
            'cpapiuser', 'cpapisecret',
            // auth_econcordia
            'jwt_key', 'token_validation_url', 'login_validation_url', 'host',
            // Moodle features
            'enablestats', 'allowindexing', 'allowguestmymoodle', 'debug', 'debugdisplay', 'perfdebug', 'debugstringids', 'debugvalidators', 'debugpageinfo', 'loglifetime',
            // Cron
            'lastcroninterval', 'lastcronstart',
            // H5P
            'site_uuid', 'recentfetch', 'recentresponse',
            // custom theme
            'adfsurl'
        );

        foreach ($objCmdLineOutput as $name => $set) {
            if (!in_array($name, $settingsToIgnore)) {
                // Create the command to set the value.
                $commands .= sprintf(
                    "%s admin/cli/cfg.php --component=%s --name=%s --set=%s\n",
                    $php, $component, $name, escapeshellarg($set)
                );

                // Display the new value for the setting when importing.
                if ($options['verbose']) {
                    $commands .= 'echo -n "' . $name . ' of ' . $component . ' is set to: "' . "\n";
                    $commands .= sprintf("%s admin/cli/cfg.php --component=%s --name=%s\n\n", $php, $component, $name);
                }
            }
        }
    }

    // Output exported module if verbose is on.
    if ($options['verbose']) {
        // Output the component being exported when in verbose mode.
        cli_writeln('Exporting : ('.$index.'/'.$totalComponents.') ' . $component, STDERR);
    }

    return $commands;
}

/**
 * Get the individual plugin name.
 *
 * @param str $extra Extra plugin to include such as core.
 *
 * @return array $components The plugins list.
 */
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
