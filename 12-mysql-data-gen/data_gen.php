<html>
    <head>
        <meta charset="utf-8"/>
        <title>Mysql数据生成器</title>
    </head>
    <body>
        <h1>Mysql数据生成器</h1>
        <form id="gen" method="post" action="<?php echo $_SERVER['PHP_SELF']; ?>">
            <table>
                <tr>
                    <td><p>语言</p></td>
                    <td>
                        <select name="lang">
                            <option value="en">英文</option>
                            <option value="cn">中文</option>
                        </select>
                    </td>
                </tr>
                <tr>
                    <td><p>主机名</p></td>
                    <td><input name="host" value="127.0.0.1" required="required" /></td>
                </tr>
                <tr>
                    <td><p>端口</p></td>
                    <td><input name="port" value="3306" required="required" /></td>
                </tr>
                <tr>
                    <td><p>用户名</p></td>
                    <td><input name="username" value="root" required="required" /></td>
                </tr>
                <tr>
                    <td><p>密码</p></td>
                    <td><input type="password" name="password" value="" /></td>
                </tr>
                <tr>
                    <td><p>数据库名</p></td>
                    <td><input name="db" value="test" required="required"/></td>
                </tr>
                <tr>
                    <td><p>表名</p></td>
                    <td><input name="table" value="test" required="required"/></td>
                </tr>
                <tr>
                    <td><p>异常回滚</p></td>
                    <td>
                        <select name="rollback">
                            <option value="0">否</option>
                            <option value="1">是</option>
                        </select>
                    </td>
                </tr>
                <tr>
                    <td><p>条数</p></td>
                    <td>
                        <select name="count">
                            <option value="1">1条</option>
                            <option value="10">10条</option>
                            <option value="100">1百条</option>
                            <option value="1000">1千条</option>
                            <option value="10000">1万条</option>
                            <option value="100000">10万条</option>
                            <option value="1000000">100万条</option>
                            <option value="10000000">1千万条</option>
                            <option value="100000000">1亿条</option>
                        </select>
                    </td>
                </tr>
                <tr>
                    <td><p>超时控制(单位：秒,默认不控制)</p></td>
                    <td><input name="limit" value="0" required="required"/></td>
                </tr>
            </table>
            <h2>列设置</h2>
            <button id="add">添加列</button>
            <table id="gen-table">
                <tr id="row">
                    <td><input id="col_name" name="data[name][]" required="required"/></td>
                    <td>
                        <select id="type_name" name="data[type][]">
                            <option></option>
                            <option value="fromTable">从其他表中选择</option>
                            <option value="userName">用户名</option>
                            <option value="password">密码</option>
                            <option value="ipv4">ip地址</option>
                            <option value="macAddress">mac地址</option>
                            <option value="file">文件地址</option>
                            <option value="name">姓名</option>
                            <option value="sex">性别</option>
                            <option value="company">公司</option>
                            <option value="phoneNumber">电话</option>
                            <option value="datetime">日期</option>
                            <option value="email">Email</option>
                            <option value="country">国家</option>
                            <option value="region">地区</option>
                            <option value="address">地址</option>
                            <option value="timezone">时区</option>
                            <option value="url">url</option>
                            <option value="bank">银行</option>
                            <option value="bankAccountNumber">信用卡帐号</option>
                            <option value="color">颜色</option>
                            <option value="uuid">uuid</option>
                            <option value="md5">md5</option>
                            <option value="sha1">sha1</option>
                            <option value="sha256">sha256</option>
                        </select>
                    </td>
                    <td><input class="table_edit" name="table_name" type="hidden"/></td>
                    <td><a href="#" class="remove">删除</a></td>
                </tr>
            </table>
            <button type="submit">导出</button>
        </form>
        <script src="http://cdn.bootcss.com/jquery/2.2.1/jquery.min.js"></script>
        <script>
            $(function(){
                $("#add").click(function(e) {
                    e.preventDefault();
                    var node = $("#row").clone();
                    node.find("#col_name").attr("name", "data[name][]");
                    node.find("#type_name").attr("name", "data[type][]");
                    $("#gen-table").append(node);
                    $(".remove").click(function(e){
                        $(this).parent().parent().remove();
                    });
                });
                $("#type_name").change(function(e) {
                    if (e.target.value === 'fromTable') {
                        $(this).parent().next().find("input").style('display', 'block');
                    }
                });
            });
        </script>
    </body>
</html>

<?php

require __DIR__ . '/vendor/autoload.php';

use Faker\Factory;

if (isset($_POST['data']))
{ 
    $lang     = $_POST['lang'];
    $host     = $_POST['host'];
    $port     = $_POST['port'];
    $user     = $_POST['username'];
    $passwd   = $_POST['password'];
    $db       = $_POST['db'];
    $table    = $_POST['table'];
    $cols     = $_POST['data']['name'];
    $types    = $_POST['data']['type'];
    $count    = intval($_POST['count']) < 100000000? intval($_POST['count']) : 1;
    $rollback = $_POST['rollback'];
    $limit    = intval($_POST['limit']);

    if ($lang == 'cn')
    {
        $faker = Faker\Factory::create('zh_CN');
    } else {
        $faker = Faker\Factory::create();
    }

    $custom_fake = [
        'datetime' => function () use ($faker) {
            return $faker->dateTime($max = 'now', $timezone = date_default_timezone_get())->format('Y:m:d H:i:s');
        },
        'sex' => function () use ($lang) {
            if ($lang == 'cn') {
                $sexs = ['男', '女'];
            } else {
                $sexs = ['male', 'female'];
            }
            return $sexs[array_rand($sexs)];
        }
    ];

    function getValsByTypes() {
        global $faker;
        global $lang;
        global $types;
        global $custom_fake;

        $values = [];
        foreach ($types as $key => $type) {
            if (in_array($type, array_keys($custom_fake))) {
                $val = $custom_fake[$type]();
            } else {
                $val = call_user_func_array(array($faker, $type), array());
            }
            $values[] = '"' . $val . '"';
        }
        return $values;
    }

    $connect_str = sprintf('mysql:host=%s;port=%s;dbname=%s', $host, $port, $db);

    try {
        $pdo = new PDO($connect_str, $user, $passwd, array(
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
        ));
    } catch (Exception $e) {
        exit('数据库连接失败');
    }

    $base_sql = sprintf('INSERT INTO %s (%s) VALUES ',
        $table,
        implode(',', $cols)
    );

    $loop_times  = ($count / 1000) > 1? ($count / 1000) : 1;
    $combine_len = ($count / 1000) > 1? 1000 : intval($count);
    $progress    = 0;
    if ($limit) {
        set_time_limit($limit);
    } else {
        set_time_limit(0);
    }

    $pdo->beginTransaction();

    try {
        $start_time = microtime(true);
        for ($t = 0; $t < $loop_times; $t++) {
            $sqls = [];
            for ($i = 0; $i < $combine_len; $i++) {
                $sqls[] = sprintf('(%s)', implode(',', getValsByTypes($types)));
            }
            $i_sql  = $base_sql . implode(',', $sqls) . ';';
            $stmt   = $pdo->prepare($i_sql);
            $status = $stmt->execute();
            unset($sqls);
            $progress += $combine_len;
        }
        $pdo->commit();
    } catch(Exception $e) {
        if ($rollback) {
            $pdo->rollback();
            exit('发生异常，执行回滚');
        }
        echo '发生异常，异常信息：' . $e->getMessage();
    } finally {
        $end_time = microtime(true);
        echo "执行完成，执行了" . $progress . "个语句。耗时：" . ($end_time - $start_time) . '秒';
    }
}
?>