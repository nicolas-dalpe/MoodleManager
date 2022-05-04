<?php
define('CLI_SCRIPT', true);
require('config.php');
require('lib/clilib.php');

$usage = "

php cfg_manage.php --export --modules=core > settings.txt
Exports modules as JSON objects.
--modules can be:
 - core: Return only core module
 - contrib: Returns only the contributed module
 - module: Module name, can be csv ie: quiz,page,h5p
 - all: Returns all modules

php cfg_manage.php --import --file=settings.txt
Import the settings contained in file.

";

list($options, $unrecognized) = cli_get_params(
    [
        'export'  => false,
        'import'  => false,
        'file'    => false,
        'modules' => false,
        'help'    => false
    ]
);

// Param check.
if ($options['help']) {
    exit($usage);
} else if ($options['export'] == false && $options['import'] === false) {
    exit($usage);
} else if ($options['export'] == true && $options['modules'] === false) {
    exit($usage);
} else if ($options['import'] == true && $options['file'] === false) {
    exit($usage);
}

if ($options['export']) {
    $Export = new Export($options);
    echo $Export->get_json();
}

if ($options['import']) {
    $Import = new Import($options);
}

/**
 * Evironment variables.
 */
class Env {

    /** @var string $php Path to PHP. */
    public $php = '/usr/local/bin/php';
}

/**
 * Export Moodle's settings as a json object.
 */
class Export extends Env {

    /** @var string $module The modules name to export. */
    private $modules;

    /** @var object $output The terminal output class. */
    private $output;

    public function __construct(array $options) {
        $this->output = new Output();
        $this->set_modules($options['modules']);
    }

    /**
     * Set the modules name to export.
     *
     * @param string $modules The modules name to export.
     */
    private function set_modules($modules) {
        if (!empty($modules) && strlen($modules) > 2) {
            $this->modules = explode(',', $modules);
        }
    }

    public function get_json() {

        // Contains the output of the cfg.php.
        $cmdLineOutput = array();

        // Contains all the JSON setting strings of module to export.
        $settings = array();

        // Get all the modules if --modules == all.
        if ($this->modules[0] == 'all') {
            $this->modules = $this->get_all_modules('core');
        }

        // Get all the modules if --modules == all.
        if ($this->modules[0] == 'contrib') {
            $this->modules = $this->get_all_modules();
        }

        $total_modules = count($this->modules);

        $current_module = 1;

        foreach($this->modules as $module) {

            // Get the cfg.php Moodle script to output the component settings in JSON format.
            // We export the settings in JSON so it is easier to manage the multi-line settings.
            exec($this->php.' admin/cli/cfg.php --component='.$module.' --json', $cmdLineOutput, $status);

            if ($status === 0) {

                // Do not keep the component if it only has a version setting and no other settings.
                $objCmdLineOutput = json_decode($cmdLineOutput[0]);
                if (count(get_object_vars($objCmdLineOutput)) == 1 && isset($objCmdLineOutput->version)) {

                    // Output the component being skipped.
                    $this->output->line('Skipped: ' . $module);

                    continue;
                }

                // Wrap json in our own structure ("module:{settings:...}").
                $settings[] = '"' . $module . '":' . $cmdLineOutput[0];
            }

            // Output the component being exported.
            $this->output->line($current_module.'/'.$total_modules.' - Exported: ' . $module . '.');

            $current_module++;

            unset($cmdLineOutput);
        }

        return "{\n" . implode(",\n", $settings) . "\n}";
    }

    /**
     * Get the individual plugin name.
     *
     * @param str $extra Extra plugin to include such as core.
     *
     * @return array $components The plugins list.
     */
    private function get_all_modules($extra = false) {
        global $CFG, $DB;

        // Contains the list of components to return.
        $components = array();

        // Add special request to the list.
        if ($extra !== false) {
            $components[] = $extra;
        }

        $plugins = $DB->get_records_sql("SELECT * FROM {$CFG->prefix}config_plugins GROUP BY plugin");
        foreach ($plugins as $plugin) {
            $components[] = $plugin->plugin;
        }

        return $components;
    }
}

class Import extends Env {

    public function __construct(array $options) {
        $this->output = new Output();
        $this->set_file($options['file']);
    }

    public function set_file(string $file) {
        if (!empty($file) && strlen($file) > 3) {
            $this->file = $file;
        }
    }

    public function import() {
        $json = file_get_contents($this->file);
        $settings = json_decode($json);
        var_dump($settings);
        exit();
    }
}

class Output extends Env {

    /**
     * Write a line to the terminal.
     *
     * @param str $text The text to be outputed.
     */
    public function line($text) {
        // Use the STDERR channel so the output is written to
        // the console and not the > file.
        cli_writeln($text, STDERR);
    }
}

























/*
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
    global $php, $options, $status;

    // Contains the output of the cfg.php
    $cmdLineOutput = array();

    // Contains the individual PHP commands.
    // $commands = '';
    $commands = array();

    // Get the cfg.php Moodle script to output the component settings in JSON format.
    // We export the settings in JSON so it is easier to manage the multi-line settings.
    exec($php.' admin/cli/cfg.php --component='.$component.' --json', $cmdLineOutput, $status);

    if ($status === 0) {

        $commands[$component] = $cmdLineOutput;

        // $objCmdLineOutput = json_decode($cmdLineOutput[0]);

        // Do not print the component if it only has a version setting and no other settings.
        // if (count(get_object_vars($objCmdLineOutput)) == 1 && isset($objCmdLineOutput->version)) {
        //     return "";
        // }

        // Make sure the incoming and the local components are at the same version.
        // $localVersion = $DB->get_record('config_plugins', ['plugin' => $component, 'name' => 'version']);
        // if ($localVersion->version == $objCmdLineOutput->version) {
        //     return "";
        // }

        $settingsToIgnore = array(
            // Core
            'siteidentifier', 'supportemail', 'siteadmins', 'themerev', 'jsrev', 'langrev', 'localcachedirpurged',
            'scheduledtaskreset', 'allversionshash', 'fileslastcleanup', 'digestmailtimelast', 'scorm_updatetimelast',
            'templaterev', 'noemailever', 'auth', 'enrol_plugins_enabled',
            // Core - database
            'dbtype', 'dblibrary', 'dbhost', 'dbname', 'dbuser', 'dbpass', 'prefix', 'wwwroot',
            // Core - file permissions
            'directorypermissions', 'dirroot', 'filepermissions', 'umaskpermissions',
            // Core - path
            'dataroot', 'libdir', 'tempdir', 'backuptempdir', 'cachedir', 'localcachedir', 'localrequestdir',
            'langotherroot', 'langlocalroot', 'noreplyaddress', 'chat_serverhost', 'pathtogs', 'geoip2file', 'auth_instructions',
            // Core - OS path
            'pathtounoconv',
            // Core - SMTP
            'smtphosts', 'smtpsecure', 'smtpauthtype', 'smtpuser', 'smtppass', 'smtpmaxbulk',
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
            'enablestats', 'allowindexing', 'allowguestmymoodle', 'debug', 'debugdisplay', 'perfdebug',
            'debugstringids', 'debugvalidators', 'debugpageinfo', 'loglifetime',
            // Cron
            'lastcroninterval', 'lastcronstart',
            // H5P
            'site_uuid', 'recentfetch', 'recentresponse',
            // custom theme
            'adfsurl'
        );

        // foreach ($objCmdLineOutput as $name => $set) {
        //     if (!in_array($name, $settingsToIgnore)) {
        //         // Create the command to set the value.
        //         $commands .= sprintf(
        //             "%s admin/cli/cfg.php --component=%s --name=%s --set=%s\n",
        //             $php, $component, $name, escapeshellarg($set)
        //         );

        //         // Display the new value for the setting when importing.
        //         if ($options['verbose']) {
        //             $commands .= 'echo -n "' . $name . ' of ' . $component . ' is set to: "' . "\n";
        //             $commands .= sprintf("%s admin/cli/cfg.php --component=%s --name=%s\n\n", $php, $component, $name);
        //         }
        //     }
        // }
    }

    // Output exported module if verbose is on.
    if ($options['verbose']) {
        // Output the component being exported when in verbose mode.
        cli_writeln('Exporting : ' . $component . ' --> Done.', STDERR);
    }

    return $commands;
}

/**
 * Get the individual plugin name.
 *
 * @param str $extra Extra plugin to include such as core.
 *
 * @return array $components The plugins list.
 *
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
*/