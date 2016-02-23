<?php

/**
 * Created by PhpStorm.
 * User: mofan
 * Date: 2016/1/20 0020
 * Time: 10:28
 */


class SchemaTool {

	static $verbose = 1;
	const COPY_PAGE_SIZE = 5000;

	static public function addField($tableCreateSql, $schema, mysqli $mysqli) {

		set_time_limit(99999999);


		$table = '';
		if (!self::runVerbose('parse create sql',
			function()use($tableCreateSql, &$schema, &$table){
				if (!self::parseCreateSql($tableCreateSql, $schema, $table)) {
					self::debugIndent("can not parse schema and table from given create sql");
					return false;
				}
				return true;
			}
		)) {
			return false;
		}


		if (!self::runVerbose("check no table named `$schema`.`{$table}_old`",
			function()use($mysqli, $schema, $table){
				if (!$mysqli->real_query("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE
					TABLE_SCHEMA='$schema' AND TABLE_NAME='{$table}_old'")
				) {
					self::debugIndent($mysqli->error);
					return false;
				}
				$result = $mysqli->store_result();
				$row = $result->fetch_assoc();
				if ($row) {
					self::debugIndent("table `$schema`.`{$table}_old` exist");
					return false;
				}
				return true;
			}
		)) {
			return false;
		}


		$oldPKField = '';
		$oldFields = array();
		self::debug("read old table fields  [ start ]");
		if (!self::readFieldsAndPK($mysqli, $schema, $table, $oldFields, $oldPKField)) {
			self::debug("read old table fields  [ failed ]");
			return false;
		}else{
			self::debug("read old table fields  [ ok ]");
		}


		$tableNew = $table.'_new';


		$tableCreateSql = preg_replace("/$table/", $tableNew, $tableCreateSql, 1);
		self::debug("create new table  [ start ]");
		if (!self::createTable($mysqli, $tableCreateSql, $schema)) {
			self::debug("create new table  [ failed ]");
			return false;
		} else {
			self::debug("create new table  [ ok ]");
		}


		$newPKField = '';
		$newFields = array();
		self::debug("read new table fields  [ start ]");
		if (!self::readFieldsAndPK($mysqli, $schema, $tableNew, $newFields, $newPKField)) {
			self::removeUnuseTable($schema, $tableNew, $mysqli);
			self::debug("read new table fields  [ failed ]");
			return false;
		} else {
			self::debug("read new table fields  [ ok ]");
		}


		if (!self::runVerbose('check primary key are same',
			function()use($mysqli, $schema, $tableNew, $newPKField, $oldPKField){
				if ($newPKField==''||$oldPKField==''||$newPKField!=$oldPKField) {
					return false;
				}
				return true;
			}
		)) {
			self::removeUnuseTable($schema, $tableNew, $mysqli);
			return false;
		}


		if (!self::runVerbose('check no fields missing',
			function()use($oldFields, $newFields, $schema, $tableNew, $mysqli){
				$arr = array_diff($oldFields, $newFields);
				if (!empty($arr)) {
					self::debugIndent("some fields missing");
					return false;
				}
				return true;
			}
		)) {
			self::removeUnuseTable($mysqli, $schema, $tableNew);
			return false;
		}


		self::debug("create trigger `$schema`.`after_{$table}_insert`  [ start ]");
		if (!self::createInsertTrigger($mysqli, $schema, $table, $tableNew, $oldFields)) {
			self::removeUnuseTable($mysqli, $schema, $tableNew);
			self::debug("create trigger `$schema`.`after_{$table}_insert`  [ failed ]");
			return false;
		}else{
			self::debug("create trigger `$schema`.`after_{$table}_insert`  [ ok ]");
		}


		self::debug("create trigger `$schema`.`after_{$table}_update`  [ start ]");
		if (!self::createUpdateTrigger($mysqli, $schema, $table, $tableNew, $oldFields)) {
			self::removeTriggers($mysqli, $schema, $table);
			self::removeUnuseTable($mysqli, $schema, $tableNew);
			self::debug("create trigger `$schema`.`after_{$table}_update`  [ failed ]");
			return false;
		} else {
			self::debug("create trigger `$schema`.`after_{$table}_update`  [ ok ]");
		}


		$currentMaxPkValue = '';
		self::debug("get current max pk value  [ start ]");
		if (!self::getCurrentMaxPKV($mysqli, $oldPKField, $schema, $table, $currentMaxPkValue)) {
			self::removeTriggers($mysqli, $schema, $table);
			self::removeUnuseTable($mysqli, $schema, $tableNew);
			self::debug("get current max pk value  [ failed ]");
			return false;
		} else {
			self::debug("get current max pk value  [ ok ]");
		}


		if (!$currentMaxPkValue) { // nothing to copy
			self::removeTriggers($mysqli, $schema, $table);
			self::removeUnuseTable($mysqli, $schema, $tableNew);
			return true;
		}


		self::debug("got current max pk value: $currentMaxPkValue");


		self::debug("copy data  [ start ]");
		if (!self::copyData($mysqli, $currentMaxPkValue, $schema, $table, $tableNew, $oldFields, $oldPKField)) {
			self::removeTriggers($mysqli, $schema, $table);
			self::removeUnuseTable($mysqli, $schema, $tableNew);
			self::debug("copy data  [ failed ]");
			return false;
		}else{
			self::debug("copy data  [ ok ]");
		}


		self::debug("check data rows  [ start ]");
		if (!self::checkRows($mysqli, $schema, $table, $tableNew, $oldPKField, $currentMaxPkValue)) {
			self::removeTriggers($mysqli, $schema, $table);
			self::removeUnuseTable($mysqli, $schema, $tableNew);
			self::debug("check data rows  [ failed ]");
			return false;
		}else{
			self::debug("check data rows  [ ok ]");
		}


		self::debug("rename $table=>{$table}_old,$tableNew=>$table  [ start ]");
		if (!self::renameTable($mysqli, $schema, $table, $tableNew)) {
			self::debug("rename $table=>{$table}_old,$tableNew=>$table  [ failed ]");
			return false;
		}else{
			self::debug("rename $table=>{$table}_old,$tableNew=>$table  [ ok ]");
		}


		if (!self::runVerbose("clean up",
			function()use($mysqli, $schema, $table, $tableNew){
				self::removeTriggers($mysqli, $schema, $table);
				self::removeUnuseTable($mysqli, $schema, $tableNew);
				return true;
			}
		)) {
			return false;
		}


		self::debug("all work well done!!!");
		return true;
	}

	static public function createTable(mysqli $mysqli, $tableCreateSql, $schema){
		if (!$mysqli->select_db($schema)) {
			self::debugIndent("can not select db: {$mysqli->error}");
			return false;
		}
		if (!$mysqli->real_query($tableCreateSql)) {
			self::debugIndent("create table failed: {$mysqli->error}");
			return false;
		}
		return true;
	}

	static public function readFieldsAndPK(mysqli $mysqli, $schema, $table, &$fields, &$pkField){
		if (!$mysqli->real_query("DESCRIBE `$schema`.`$table`")) {
			self::debugIndent($mysqli->error);
			return false;
		}
		$result = $mysqli->store_result();
		while ($row = $result->fetch_assoc()) {
			if ($pkField=='' && $row['Key']=='PRI') {
				$pkField = $row['Field'];
			}
			$fields[] = $row['Field'];
		}
		if (empty($fields)) {
			self::debugIndent("can not get fields of $schema.$table");
			return false;
		}
		return true;
	}

	static public function createInsertTrigger(mysqli $mysqli, $schema, $table, $tableNew, $fields){
		$sql = "CREATE TRIGGER `$schema`.`after_{$table}_insert` AFTER insert ";
		$sql .= "ON `$schema`.`$table` ";
		$sql .= "FOR EACH ROW BEGIN ";
		$sql .= "replace into `$schema`.`$tableNew` ";
		$sql .= "(`";
		$sql .= implode('`,`', $fields);
		$sql .= "`)";
		$sql .= "values";
		$sql .= "(";
		$sql .= implode(',', array_map(function($s){return 'new.'.$s;}, $fields));
		$sql .= ");";
		$sql .= "END";
		if (!$mysqli->real_query($sql)) {
			self::debugIndent($mysqli->error);
			return false;
		}
		return true;
	}

	static public function createUpdateTrigger(mysqli $mysqli, $schema, $table, $tableNew, $fields){
		$sql = "CREATE TRIGGER `$schema`.`after_{$table}_update` AFTER update ";
		$sql .= "ON `$schema`.`$table` ";
		$sql .= "FOR EACH ROW BEGIN ";
		$sql .= "replace into `$schema`.`$tableNew` ";
		$sql .= "(`";
		$sql .= implode('`,`', $fields);
		$sql .= "`)";
		$sql .= "values";
		$sql .= "(";
		$sql .= implode(',', array_map(function($s){return 'new.'.$s;}, $fields));
		$sql .= ");";
		$sql .= "END";
		if (!$mysqli->real_query($sql)) {
			self::debugIndent($mysqli->error);
			return false;
		}
		return true;
	}

	static public function getCurrentMaxPKV(mysqli $mysqli, $pkField, $schema, $table, &$outPutMaxPkValue){
		if (!$mysqli->real_query("select count(*) as cnt from `$schema`.`$table`")) {
			self::debugIndent($mysqli->error);
			return false;
		}
		$result = $mysqli->store_result();
		$row = $result->fetch_assoc();
		if ($row['cnt'] == 0) {
			self::debugIndent("nothing to copy");
			return true;
		}
		if (!$mysqli->real_query("select $pkField from `$schema`.`$table` order by $pkField desc limit 1")) {
			self::debugIndent($mysqli->error);
			return false;
		}
		$result = $mysqli->store_result();
		$row = $result->fetch_assoc();
		if (!$row) {
			self::debugIndent("currentMaxPkValue not found");
			return false;
		}
		$outPutMaxPkValue = $row[$pkField];
		return true;
	}

	static public function renameTable(mysqli $mysqli, $schema, $table, $tableNew){
		if (!$mysqli->real_query(
			"RENAME TABLE
				 	`$schema`.`$table` TO `$schema`.`{$table}_old`,
				 	`$schema`.`$tableNew` TO `$schema`.`$table`"
		)) {
			self::debugIndent($mysqli->error);
			return false;
		}
		return true;
	}

	static public function checkRows(mysqli $mysqli, $schema, $table, $tableNew, $pkField, $maxPkValue) {
		if (!$mysqli->real_query("select count(*) as cnt from `$schema`.`$table` where $pkField<=$maxPkValue")) {
			self::debugIndent($mysqli->error);
			return false;
		}
		$result = $mysqli->store_result();
		$row = $result->fetch_assoc();
		$oldRows = $row['cnt'];
		if (!$mysqli->real_query("select count(*) as cnt from `$schema`.`$tableNew` where $pkField<=$maxPkValue")) {
			self::debugIndent($mysqli->error);
			return false;
		}
		$result = $mysqli->store_result();
		$row = $result->fetch_assoc();
		if ($row['cnt']!=$oldRows || $oldRows<1) {
			self::debugIndent("rows count where $pkField<=$maxPkValue are different $oldRows||{$row['cnt']}");
			return false;
		}
		return true;
	}

	static public function copyData(mysqli $mysqli, $maxPkValue, $schema, $table, $tableNew, $fields, $pkField) {
		if (!$mysqli->real_query("select count(*) as cnt from `$schema`.`$table` where $pkField<=$maxPkValue")) {
			self::debugIndent($mysqli->error);
			return false;
		}
		$result = $mysqli->store_result();
		$row = $result->fetch_assoc();
		if (!$row) {
			self::debugIndent($mysqli->error);
			return false;
		}
		$total = $row['cnt'];
		$pageSize = self::COPY_PAGE_SIZE;
		self::debugIndent("total rows: $total");
		$strFields = implode(',', $fields);
		$maxPKV = $maxPkValue;
		while(1) {
			if (!$mysqli->real_query("SELECT MIN(A.$pkField) as minpkv, MAX(A.$pkField) as maxpkv FROM
					(SELECT $pkField FROM `$schema`.`$table` WHERE $pkField<=$maxPKV ORDER BY $pkField DESC
					LIMIT $pageSize) AS A")
			) {
				self::debugIndent($mysqli->error);
				return false;
			}
			if (!$result = $mysqli->store_result()) {
				self::debugIndent($mysqli->error);
				return false;
			}
			if (!$row = $result->fetch_assoc()) {
				break;
			}
			if (!$mysqli->real_query("insert ignore into `$schema`.`$tableNew`($strFields)
					select $strFields from `$schema`.`$table` where $pkField between {$row['minpkv']} and {$row['maxpkv']}")
			) {
				self::debugIndent($mysqli->error);
				return false;
			}

			$maxPKV = $row['minpkv'];

			$total -= $mysqli->affected_rows;

			if ($row['minpkv'] == $row['maxpkv']) {
				self::debugIndent('remain rows: 0');
				break;
			}else{
				self::debugIndent('remain rows: '. $total);
			}

			usleep(1000);//稍微歇一会儿，给别人点机会
		}
		return true;
	}

	static public function removeTriggers(mysqli $mysqli, $schema, $table) {
		if($mysqli->real_query("drop trigger IF EXISTS `$schema`.`after_{$table}_insert`")){
			self::debugIndent("trigger `$schema`.`after_{$table}_insert` removed");
		}
		if($mysqli->real_query("drop trigger IF EXISTS `$schema`.`after_{$table}_update`")){
			self::debugIndent("trigger `$schema`.`after_{$table}_update` removed");
		}
	}

	static public function removeUnuseTable(mysqli $mysqli, $schema, $table) {
		if (self::dropTable($schema, $table, $mysqli)) {
			self::debugIndent("table `$schema`.`$table` droped");
		}
	}

	static protected function runVerbose($doing, $cb) {
		self::debug($doing.	   '  [ start ]');
		$ret = $cb();
		if ($ret===false) {
			self::debug($doing.'  [ failed ]');
		}else{
			self::debug($doing.'  [ ok ]');
		}
		return $ret;
	}

	static protected function debug($msg) {
		if(self::$verbose) {
			echo trim($msg)."\n";
		}
	}

	static protected function debugIndent($msg) {
		if (self::$verbose) {
			echo '    '.trim($msg)."\n";
		}
	}

	static public function dropTable($schema, $table, mysqli $mysqli) {
		return $mysqli->real_query("DROP TABLE IF EXISTS `$schema`.`$table`");
	}

	static public function parseCreateSql($tableCreateSql, &$schema, &$table) {
		if (!preg_match('/CREATE\s+TABLE\s+([\w\.\`]+)/is', $tableCreateSql, $m)) {
			return false;
		}

		$str = str_replace('`', '', $m[1]);
		$arr = array_filter(explode('.', $str));
		if (empty($arr)) {
			return false;
		}

		if (isset($arr[1])) {
			$schema = $arr[0];
			$table = $arr[1];
		}else{
			$table = $arr[0];
		}

		return true;
	}

	/**
	 * @param mysqli $mysqli
	 * @return array|false
	 */
	static public function getAllDBSize(mysqli $mysqli) {
		$sql = "SELECT
			TABLE_SCHEMA AS db_name,
			CONCAT(TRUNCATE(SUM(data_length)/1024/1024,2),' MB') AS data_size,
			CONCAT(TRUNCATE(SUM(index_length)/1024/1024,2),'MB') AS index_size
		FROM information_schema.tables
		GROUP BY TABLE_SCHEMA
		ORDER BY data_length DESC";
		if (!$mysqli->real_query($sql)) {
			if (self::$verbose) {
				echo 'getAllDBSize failed:'. $mysqli->error ."\n";
			}
			return false;
		}
		$rs = array();
		$result = $mysqli->store_result();
		while($row = $result->fetch_assoc()) {
			$rs[] = $row;
		}

		return $rs;
	}

	static public function getDBSize($dbname, mysqli $mysqli) {
		$sql = "SELECT
			TABLE_SCHEMA AS db_name,
			CONCAT(TRUNCATE(SUM(data_length)/1024/1024,2),' MB') AS data_size,
			CONCAT(TRUNCATE(SUM(index_length)/1024/1024,2),'MB') AS index_size
		FROM information_schema.tables WHERE TABLE_SCHEMA='$dbname'
		GROUP BY TABLE_SCHEMA
		ORDER BY data_length DESC";
		if (!$mysqli->real_query($sql)) {
			if (self::$verbose) {
				echo 'getDBSize failed:'. $mysqli->error ."\n";
			}
			return false;
		}

		$result = $mysqli->store_result();
		if ($row = $result->fetch_assoc()) {
			return $row;
		}

		if (self::$verbose) {
			echo "Schema $dbname not exist\n";
		}

		return false;
	}

}


///////////////////////main/////////////////////////
if (!isset($argv[4])) {
	echo $argv[0].' host user psw path2createSqlFile [copy]';
	exit(1);
}
$host = $argv[1];
$user = $argv[2];
$psw = $argv[3];
$sqlFile = $argv[4];


$mysqli = new mysqli();
$mysqli->real_connect($host, $user, $psw, null, null);

$createSql = rtrim(file_get_contents($sqlFile), ';');
if (isset($argv[5]) && $argv[5]=='copy') {
	$schema = '';
	$table = '';
	$fields = array();
	$pkField = '';
	if (
		SchemaTool::parseCreateSql($createSql, $schema, $table) &&
		SchemaTool::readFieldsAndPK($mysqli, $schema, $table, $fields, $pkField)
	){
		$maxPKV = '';
		if (!$mysqli->real_query("select $pkField from `$schema`.`{$table}_new` order by $pkField asc limit 1")) {
			echo $mysqli->error."\n";
		}
		$result = $mysqli->store_result();
		$row = $result->fetch_assoc();
		$maxPKV = $row[$pkField];
		if (!$maxPKV) {
			echo "read current mini pk value failed\n";
			exit(1);
		}else{
			echo "current mini pk value : $maxPKV\n";
		}
		$r = SchemaTool::copyData($mysqli, $maxPKV, $schema, $table, $table.'_new', $fields, $pkField);
		if ($r) {
			echo "check rows  [ start ]\n";
			$r = SchemaTool::checkRows($mysqli, $schema, $table, $table.'_new', $pkField, $maxPKV);
			if ($r) {
				echo "check rows  [ ok ]\n";
				$r = SchemaTool::renameTable($mysqli, $schema, $table, $table.'_new');
				if ($r) {
					SchemaTool::removeTriggers($mysqli, $schema, $table);
				}
			}else{
				echo "check rows  [ failed ]\n";
			}
		}
	}
} else {
	$r = SchemaTool::addField($createSql, 'testa', $mysqli);
}
$mysqli->close();


exit($r?0:1);